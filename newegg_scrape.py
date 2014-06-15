#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lxml.html import parse, tostring
from urllib2 import urlopen
from lxml.html import builder as E
import re
from models import session, Data, table_name

URL = "http://www.newegg.com/Special/Rebate.aspx?RebateType=2&ExpiredRebate=1&Subcategory=0&Brand=0&saveCompare=0&SaveAmount=&item=&action=search"

class Item:
    """Item class which holds details about a list item"""

    def __init__(self, el):
        self.el = el
        self.parse()

    def parse( self ):
        """Parses a row element and populates the property variables"""
        import re
        from urlparse import parse_qsl


        #TODO: Add check for proper layout before parsing

        self.description = self.el[1].text_content().strip()
        self.inStock = self.el[3].text_content().strip()
        self.shipping = self.el[4].text_content().strip()
        self.price = self.el.cssselect('span.dred')[0].text_content().strip()
        self.rebateTxt = self.el.cssselect('td.mirRebate')[0].text_content().strip()

        m = re.search('\$[\d.]+', self.rebateTxt)
        if m:
            self.rebate = m.group(0)
        else:
            raise RuntimeError, "Unable to parse rebate"

        self.link = self.el[1].cssselect('a')[0].get('href')
        self.itemNo = parse_qsl(self.link)[0][1]

        self.instantRebate = self.getInstantRebate()

        price_f = float( self.price.strip('$').replace(',','') )
        rebate_f = float( self.rebate.strip('$').replace(',','') )
        if self.instantRebate == '-':
            instant_rebate_f = 0.0
        else:
            instant_rebate_f = float(
                               self.instantRebate.strip('$').replace(',',''))
        self.finalPrice = '$%.2f' % (price_f - rebate_f - instant_rebate_f)


    def getInstantRebate(self):
        from lxml.html import parse
        from urllib2 import urlopen
        URL = "http://www.newegg.com/Special/Rebate.aspx?RebateType=1&ExpiredRebate=1&Subcategory=0&Brand=0&saveCompare=0&SaveAmount=&item=%s&action=search"
        item_url = URL % self.itemNo
        root = parse( urlopen( item_url ) ).getroot()
        if not root.cssselect('table.ftb tr.listRowOdd'):
           return '-'

        tr = root.cssselect('table.ftb tr.listRowOdd')[0]
        instRebateTxt = tr.cssselect('td.mirRebate')[0].text_content().strip()

        m = re.search('\$[\d.]+', instRebateTxt)
        if m:
           return  m.group(0)
        else:
           raise RuntimeError, "Unable to parse rebate |%s|" % item_url


    # def renderTD(self):
    #     cols = [ E.TD( E.A(self.description, href=self.link) ),
    #              E.TD(self.inStock), E.TD(self.shipping),E.TD(self.price),
    #                          E.TD(self.rebate),  E.TD(self.instantRebate),
    #                             E.TD(self.finalPrice), E.TD(self.itemNo) ]
    #     return E.TR( *cols )

    def saveOneRow(self):
        data = Data(description=self.description.encode('utf-8'), link=self.link, stock=self.inStock.encode('utf-8'),
                    shipping=self.shipping.encode('utf-8'), price=self.price.encode('utf-8'),
                    mail_rebate=self.rebate.encode('utf-8'), instant_rebate=self.instantRebate.encode('utf-8'),
                    final_price=self.finalPrice.encode('utf-8'), item_number=self.itemNo.encode('utf-8'))

        session.add(data)
        session.commit()

if __name__ == "__main__":
    page = 1
    print "Parsing page #01"
    root = parse( urlopen( URL ) ).getroot()
    rows = [ E.TR( E.TD('Description'), E.TD('Stock'), E.TD('Shipping'),
                                  E.TD('Price'), E.TD('Mail-in Rebate'),
                            E.TD('Instant Rebate'), E.TD('Final Price'),
                                                  E.TD('Item Number'))]

    while True:
        page += 1
        for tr in root.cssselect('table.ftb tr')[1:-2] :
            it = Item(tr)
            # rows.append( it.renderTD )
            it.saveOneRow()
        nextPage = None
        for a in root.cssselect('div.pagination ul li a'):
            if a.text_content().startswith('>'):
                m = re.search(',(\d+)\);', a.get('href') )
                if m:
                    nextPage = m.group(1)
                    break
        if nextPage:
            print "Parsing page #%02d" % page
            root = parse( urlopen(URL + "&Page=" + nextPage) ).getroot()
        else:
            break

    # outputHtml = E.HTML( E.HEAD(
    #                 E.LINK(rel="stylesheet", href="newEggTable.css",
    #                                                    type="text/css"),
    #                 E.TITLE("NewEgg Items")),
    #                 E.BODY(E.TABLE(E.CLASS("newEggTable"), *rows ))
    #             )
    #
    # with open('newegg.html', 'wb') as f:
    #     f.write( tostring( outputHtml, pretty_print = True, method="html") )

    print "newegg data saved to database with name %s" % table_name




