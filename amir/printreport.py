import pygtk
import gtk
import pango
import pangocairo
import logging

import utility

class PrintReport:
    def __init__(self, content, cols_width, heading=None):
        self.operation = gtk.PrintOperation()
        self.lines_per_page = 24
        self.cell_margin = 4
        self.page_margin = 5
        self.line = 2
        self.row_height = 25

        #self.headerlines = 7
        self.header_height = 0
        self.heading_height = 35
        
        self.content = content
        self.cols_width = cols_width
        self.heading = heading
        self.operation.connect("begin_print", self.beginPrint)
        self.operation.connect("draw-page", self.printPage)
        self.type = 0
        self.title = ""
        self.fields = {}
    
    ##self.content = data
    def setHeader (self, title, fields):
        self.title = title
        self.fields = fields
             
    def beginPrint(self, operation, context):
        pages = ((len(self.content) - 1) / self.lines_per_page ) + 1
        operation.set_n_pages(pages)
    
    def doPrint(self):
        self.operation.run(gtk.PRINT_OPERATION_ACTION_PRINT_DIALOG)
        
    def drawPage(self, operation, context, page_nr):
        pass
    
    def printPage(self, operation, context, page_nr):
        self.pangolayout = context.create_pango_layout()
        self.cairo_context = context.get_cairo_context()
        
        self.pangolayout.set_width(-1)
        self.pangocairo = pangocairo.CairoContext(self.cairo_context)
        
        self.formatHeader(context)
        getattr(self, self.drawfunction)(page_nr)
        #self.drawDailyNotebook(page_nr)
 
    def formatHeader(self, context):
        LINE_HEIGHT = 25
        MARGIN = self.page_margin
        cwidth = context.get_width()
        logging.info("Paper width: " + str(cwidth))
        cr = self.cairo_context
        
        fontsize = 12
        fdesc = pango.FontDescription("Sans")
        fdesc.set_size(fontsize * pango.SCALE)
        self.pangolayout.set_font_description(fdesc)
        
        if self.title != "":
            self.pangolayout.set_text(self.title)
            (width, height) = self.pangolayout.get_size()
            self.pangolayout.set_alignment(pango.ALIGN_CENTER)
            cr.move_to ((cwidth - width / pango.SCALE) / 2, (LINE_HEIGHT - (height/ pango.SCALE))/2)
            self.pangocairo.show_layout(self.pangolayout)
            
            cr.move_to((cwidth + width / pango.SCALE) / 2, LINE_HEIGHT+MARGIN)
            cr.line_to((cwidth - width / pango.SCALE) / 2, LINE_HEIGHT+MARGIN)
            
        LINE_HEIGHT = 20
        addh = LINE_HEIGHT+MARGIN
        fontsize = 10
        fdesc.set_size(fontsize * pango.SCALE)
        self.pangolayout.set_font_description(fdesc)
        
        flag = 1
        for k,v in self.fields.items():
            self.pangolayout.set_text(k + ": " + v)
            (width, height) = self.pangolayout.get_size()
            self.pangolayout.set_alignment(pango.ALIGN_CENTER)
            if flag == 1:
                addh += LINE_HEIGHT
                cr.move_to (cwidth - (width / pango.SCALE) - MARGIN, addh - (height/ pango.SCALE)/2)
                flag = 0
            else:
                cr.move_to ((width / pango.SCALE) + MARGIN, addh - (height/ pango.SCALE)/2)
                flag = 1
            self.pangocairo.show_layout(self.pangolayout)
            
        cr.stroke()
        self.header_height = addh + 8
            
            
    def drawDailyNotebook(self, page_nr):
        RIGHT_EDGE = 570  #(table width + PAGE_MARGIN)
        HEADER_HEIGHT = self.header_height
        HEADING_HEIGHT = self.heading_height
        PAGE_MARGIN = self.page_margin
        MARGIN = self.cell_margin
        TABLE_TOP = HEADER_HEIGHT + HEADING_HEIGHT + PAGE_MARGIN
        ROW_HEIGHT = self.row_height
        LINE = self.line
        
        cr = self.cairo_context
        fontsize = 9
        fdesc = pango.FontDescription("Sans")
        fdesc.set_size(fontsize * pango.SCALE)
        self.pangolayout.set_font_description(fdesc)
        
        #Table top line
        cr.move_to(PAGE_MARGIN, TABLE_TOP)
        cr.line_to(RIGHT_EDGE, TABLE_TOP)
        
        self.drawTableHeading()
          
        #Draw table data
        rindex = page_nr * self.lines_per_page
        offset = 0
        
        right_txt = RIGHT_EDGE
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
        
        self.pangolayout.set_text("----")
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        
        for i in range(0, 3):
            right_txt -= MARGIN + LINE
            cr.move_to (right_txt -(width / pango.SCALE), TABLE_TOP + (ROW_HEIGHT-(height / pango.SCALE))/2)
            self.pangocairo.show_layout(self.pangolayout)    
            right_txt -= self.cols_width[i]
            cr.move_to(right_txt, TABLE_TOP)
            cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
        
        right_txt -= MARGIN + LINE
        fontsize = 8
        fdesc.set_size(fontsize * pango.SCALE)
        self.pangolayout.set_font_description(fdesc)
        self.pangolayout.set_text(_("Sum of previous page"))
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        cr.move_to (right_txt -(width / pango.SCALE), TABLE_TOP + (ROW_HEIGHT-(height / pango.SCALE))/2)
        self.pangocairo.show_layout(self.pangolayout)    
        right_txt -= self.cols_width[3]
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
        
        right_txt -= MARGIN + LINE
        fontsize = 9
        fdesc.set_size(fontsize * pango.SCALE)
        self.pangolayout.set_font_description(fdesc)
        if page_nr == 0:
            self.pangolayout.set_text("0")
            self.debt_sum = 0
        else:
            self.pangolayout.set_text(utility.showNumber(self.debt_sum))
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        cr.move_to (right_txt -(width / pango.SCALE), TABLE_TOP + (ROW_HEIGHT-(height / pango.SCALE))/2)
        self.pangocairo.show_layout(self.pangolayout)    
        right_txt -= self.cols_width[4]
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
        
        right_txt -= MARGIN + LINE
        if page_nr == 0:
            self.pangolayout.set_text("0")
            self.credit_sum = 0
        else:
            self.pangolayout.set_text(utility.showNumber(self.credit_sum))
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        cr.move_to (right_txt -(width / pango.SCALE), TABLE_TOP + (ROW_HEIGHT-(height / pango.SCALE))/2)
        self.pangocairo.show_layout(self.pangolayout)    
        right_txt -= self.cols_width[5]
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
        
        addh= ROW_HEIGHT + TABLE_TOP
        try:
            while (offset < self.lines_per_page):
                row = self.content[rindex + offset]
                
                cr.move_to(RIGHT_EDGE, addh)
                cr.line_to(RIGHT_EDGE, addh+ROW_HEIGHT)
                
                right_txt = RIGHT_EDGE
                dindex = 0
                for data in row:
                    right_txt -= MARGIN+LINE
                    if dindex == 3:
                        fontsize = 8
                        fdesc.set_size(fontsize * pango.SCALE)
                        self.pangolayout.set_font_description(fdesc)
                        self.pangolayout.set_text(data)
                        (width, height) = self.pangolayout.get_size()
                        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
                        cr.move_to (right_txt -(width / pango.SCALE), addh + (ROW_HEIGHT-(height / pango.SCALE))/2)
                        self.pangocairo.show_layout(self.pangolayout)
                        fontsize = 9
                        fdesc.set_size(fontsize * pango.SCALE)
                        self.pangolayout.set_font_description(fdesc)
                    else:
                        self.pangolayout.set_text(data)
                        (width, height) = self.pangolayout.get_size()
                        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
                        cr.move_to (right_txt -(width / pango.SCALE), addh + (ROW_HEIGHT-(height / pango.SCALE))/2)
                        self.pangocairo.show_layout(self.pangolayout)
                        
                    right_txt -= self.cols_width[dindex]
                    cr.move_to(right_txt, addh)
                    cr.line_to(right_txt, addh + ROW_HEIGHT)
                    
                    dindex += 1
                    
                self.debt_sum += int(row[4].replace(",", ""))
                self.credit_sum += int(row[5].replace(",", ""))
                
                addh += ROW_HEIGHT
                offset += 1
        except IndexError:
            pass
        
        right_txt = RIGHT_EDGE
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)
        
        self.pangolayout.set_text("----")
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        
        for i in range(0, 3):
            right_txt -= MARGIN + LINE
            cr.move_to (right_txt -(width / pango.SCALE), addh + (ROW_HEIGHT-(height / pango.SCALE))/2)
            self.pangocairo.show_layout(self.pangolayout)    
            right_txt -= self.cols_width[i]
            cr.move_to(right_txt, addh)
            cr.line_to(right_txt, addh + ROW_HEIGHT)
        
        right_txt -= MARGIN + LINE
        fontsize = 8
        fdesc.set_size(fontsize * pango.SCALE)
        self.pangolayout.set_font_description(fdesc)
        self.pangolayout.set_text(_("Sum"))
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        cr.move_to (right_txt -(width / pango.SCALE), addh + (ROW_HEIGHT-(height / pango.SCALE))/2)
        self.pangocairo.show_layout(self.pangolayout)    
        right_txt -= self.cols_width[3]
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)
        
        right_txt -= MARGIN + LINE
        fontsize = 9
        fdesc.set_size(fontsize * pango.SCALE)
        self.pangolayout.set_font_description(fdesc)
        self.pangolayout.set_text(utility.showNumber(self.debt_sum))
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        cr.move_to (right_txt -(width / pango.SCALE), addh + (ROW_HEIGHT-(height / pango.SCALE))/2)
        self.pangocairo.show_layout(self.pangolayout)    
        right_txt -= self.cols_width[4]
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)
        
        right_txt -= MARGIN + LINE
        self.pangolayout.set_text(utility.showNumber(self.credit_sum))
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        cr.move_to (right_txt -(width / pango.SCALE), addh + (ROW_HEIGHT-(height / pango.SCALE))/2)
        self.pangocairo.show_layout(self.pangolayout)    
        right_txt -= self.cols_width[5]
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)
        
        cr.move_to(self.page_margin, addh + ROW_HEIGHT)
        cr.line_to(RIGHT_EDGE, addh + ROW_HEIGHT)
            
        cr.stroke()
    
    def drawSubjectNotebook(self, page_nr):
        RIGHT_EDGE = 570  #(table width + PAGE_MARGIN)
        HEADER_HEIGHT = self.header_height
        HEADING_HEIGHT = self.heading_height
        PAGE_MARGIN = self.page_margin
        MARGIN = self.cell_margin
        TABLE_TOP = HEADER_HEIGHT + HEADING_HEIGHT + PAGE_MARGIN
        ROW_HEIGHT = self.row_height
        LINE = self.line
        
        cr = self.cairo_context
        fontsize = 9
        fdesc = pango.FontDescription("Sans")
        fdesc.set_size(fontsize * pango.SCALE)
        self.pangolayout.set_font_description(fdesc)

        #Table top line
        cr.move_to(PAGE_MARGIN, TABLE_TOP)
        cr.line_to(RIGHT_EDGE, TABLE_TOP)
        
        self.drawTableHeading()
          
        #Draw table data
        rindex = page_nr * self.lines_per_page
        offset = 0
        
        right_txt = RIGHT_EDGE
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
        
        self.pangolayout.set_text("----")
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        
        for i in range(0, 2):
            right_txt -= MARGIN + LINE
            cr.move_to (right_txt -(width / pango.SCALE), TABLE_TOP + (ROW_HEIGHT-(height / pango.SCALE))/2)
            self.pangocairo.show_layout(self.pangolayout)    
            right_txt -= self.cols_width[i]
            cr.move_to(right_txt, TABLE_TOP)
            cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
        
        right_txt -= MARGIN + LINE
        fontsize = 8
        fdesc.set_size(fontsize * pango.SCALE)
        self.pangolayout.set_font_description(fdesc)
        self.pangolayout.set_text(_("Sum of previous page"))
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        cr.move_to (right_txt -(width / pango.SCALE), TABLE_TOP + (ROW_HEIGHT-(height / pango.SCALE))/2)
        self.pangocairo.show_layout(self.pangolayout)    
        right_txt -= self.cols_width[2]
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
        
        right_txt -= MARGIN + LINE
        fontsize = 9
        fdesc.set_size(fontsize * pango.SCALE)
        self.pangolayout.set_font_description(fdesc)
        if page_nr == 0:
            self.pangolayout.set_text("0")
            self.debt_sum = 0
        else:
            self.pangolayout.set_text(utility.showNumber(self.debt_sum))
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        cr.move_to (right_txt -(width / pango.SCALE), TABLE_TOP + (ROW_HEIGHT-(height / pango.SCALE))/2)
        self.pangocairo.show_layout(self.pangolayout)    
        right_txt -= self.cols_width[3]
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
        
        right_txt -= MARGIN + LINE
        if page_nr == 0:
            self.pangolayout.set_text("0")
            self.credit_sum = 0
        else:
            self.pangolayout.set_text(utility.showNumber(self.credit_sum))
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        cr.move_to (right_txt -(width / pango.SCALE), TABLE_TOP + (ROW_HEIGHT-(height / pango.SCALE))/2)
        self.pangocairo.show_layout(self.pangolayout)    
        right_txt -= self.cols_width[4]
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
        
        if page_nr == 0:
            remaining = int(self.content[0][3].replace(",", "")) - int(self.content[0][4].replace(",", ""))
            if self.content[0][5] == _("deb"):
                remaining -= int(self.content[0][6].replace(",", ""))
            else:
                remaining += int(self.content[0][6].replace(",", ""))
            if remaining > 0:
                self.diagnose = _("deb")
            else:
                if remaining == 0:
                    self.diagnose = _("equ")
                else:
                    self.diagnose = _("cre")
            self.remaining = utility.showNumber(remaining)
        
        right_txt -= MARGIN + LINE
        self.pangolayout.set_text(self.diagnose)
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        cr.move_to (right_txt -(width / pango.SCALE), TABLE_TOP + (ROW_HEIGHT-(height / pango.SCALE))/2)
        self.pangocairo.show_layout(self.pangolayout)    
        right_txt -= self.cols_width[5]
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
        
        right_txt -= MARGIN + LINE
        self.pangolayout.set_text(self.remaining)
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        cr.move_to (right_txt -(width / pango.SCALE), TABLE_TOP + (ROW_HEIGHT-(height / pango.SCALE))/2)
        self.pangocairo.show_layout(self.pangolayout)    
        right_txt -= self.cols_width[6]
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
        
        addh= ROW_HEIGHT + TABLE_TOP
        try:
            while (offset < self.lines_per_page):
                row = self.content[rindex + offset]
                
                cr.move_to(RIGHT_EDGE, addh)
                cr.line_to(RIGHT_EDGE, addh+ROW_HEIGHT)
                
                right_txt = RIGHT_EDGE
                dindex = 0
                for data in row:
                    right_txt -= MARGIN+LINE
                    if dindex == 2:
                        fontsize = 8
                        fdesc.set_size(fontsize * pango.SCALE)
                        self.pangolayout.set_font_description(fdesc)
                        self.pangolayout.set_text(data)
                        (width, height) = self.pangolayout.get_size()
                        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
                        cr.move_to (right_txt -(width / pango.SCALE), addh + (ROW_HEIGHT-(height / pango.SCALE))/2)
                        self.pangocairo.show_layout(self.pangolayout)
                        fontsize = 9
                        fdesc.set_size(fontsize * pango.SCALE)
                        self.pangolayout.set_font_description(fdesc)
                    else:
                        self.pangolayout.set_text(data)
                        (width, height) = self.pangolayout.get_size()
                        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
                        cr.move_to (right_txt -(width / pango.SCALE), addh + (ROW_HEIGHT-(height / pango.SCALE))/2)
                        self.pangocairo.show_layout(self.pangolayout)
                    right_txt -= self.cols_width[dindex]
                    cr.move_to(right_txt, addh)
                    cr.line_to(right_txt, addh + ROW_HEIGHT)
                    
                    dindex += 1
                    
                self.debt_sum += int(row[3].replace(",", ""))
                self.credit_sum += int(row[4].replace(",", ""))
                
                addh += ROW_HEIGHT
                offset += 1
            
        except IndexError:
            pass
        
        self.diagnose = self.content[rindex + offset - 1][5]
        self.remaining = self.content[rindex + offset - 1][6]
            
        right_txt = RIGHT_EDGE
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)
        
        self.pangolayout.set_text("----")
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        
        for i in range(0, 2):
            right_txt -= MARGIN + LINE
            cr.move_to (right_txt -(width / pango.SCALE), addh + (ROW_HEIGHT-(height / pango.SCALE))/2)
            self.pangocairo.show_layout(self.pangolayout)    
            right_txt -= self.cols_width[i]
            cr.move_to(right_txt, addh)
            cr.line_to(right_txt, addh + ROW_HEIGHT)
        
        right_txt -= MARGIN + LINE
        fontsize = 8
        fdesc.set_size(fontsize * pango.SCALE)
        self.pangolayout.set_font_description(fdesc)
        self.pangolayout.set_text(_("Sum"))
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        cr.move_to (right_txt -(width / pango.SCALE), addh + (ROW_HEIGHT-(height / pango.SCALE))/2)
        self.pangocairo.show_layout(self.pangolayout)    
        right_txt -= self.cols_width[2]
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)
        
        right_txt -= MARGIN + LINE
        fontsize = 9
        fdesc.set_size(fontsize * pango.SCALE)
        self.pangolayout.set_font_description(fdesc)
        self.pangolayout.set_text(utility.showNumber(self.debt_sum))
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        cr.move_to (right_txt -(width / pango.SCALE), addh + (ROW_HEIGHT-(height / pango.SCALE))/2)
        self.pangocairo.show_layout(self.pangolayout)    
        right_txt -= self.cols_width[3]
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)
        
        right_txt -= MARGIN + LINE
        self.pangolayout.set_text(utility.showNumber(self.credit_sum))
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        cr.move_to (right_txt -(width / pango.SCALE), addh + (ROW_HEIGHT-(height / pango.SCALE))/2)
        self.pangocairo.show_layout(self.pangolayout)    
        right_txt -= self.cols_width[4]
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)
        
        right_txt -= MARGIN + LINE
        self.pangolayout.set_text(self.diagnose)
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        cr.move_to (right_txt -(width / pango.SCALE), addh + (ROW_HEIGHT-(height / pango.SCALE))/2)
        self.pangocairo.show_layout(self.pangolayout)    
        right_txt -= self.cols_width[5]
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)
        
        right_txt -= MARGIN + LINE
        self.pangolayout.set_text(self.remaining)
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        cr.move_to (right_txt -(width / pango.SCALE), addh + (ROW_HEIGHT-(height / pango.SCALE))/2)
        self.pangocairo.show_layout(self.pangolayout)    
        right_txt -= self.cols_width[6]
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)
        
        cr.move_to(self.page_margin, addh + ROW_HEIGHT)
        cr.line_to(RIGHT_EDGE, addh + ROW_HEIGHT)
            
        cr.stroke()
            
    def drawDocument(self, page_nr):
        RIGHT_EDGE = 570  #(table width + PAGE_MARGIN)
        HEADER_HEIGHT = self.header_height
        HEADING_HEIGHT = self.heading_height
        PAGE_MARGIN = self.page_margin
        MARGIN = self.cell_margin
        TABLE_TOP = HEADER_HEIGHT + HEADING_HEIGHT + PAGE_MARGIN
        ROW_HEIGHT = self.row_height
        LINE = self.line
        
        cr = self.cairo_context
        fontsize = 9
        fdesc = pango.FontDescription("Sans")
        fdesc.set_size(fontsize * pango.SCALE)
        self.pangolayout.set_font_description(fdesc)

        #Table top line
        cr.move_to(PAGE_MARGIN, TABLE_TOP)
        cr.line_to(RIGHT_EDGE, TABLE_TOP)
        
        self.drawTableHeading()
          
        #Draw table data
        rindex = page_nr * self.lines_per_page
        offset = 0
        
        self.debt_sum = 0
        self.credit_sum = 0
        
        addh= TABLE_TOP
        try:
            while (offset < self.lines_per_page):
                row = self.content[rindex + offset]
                
                cr.move_to(RIGHT_EDGE, addh)
                cr.line_to(RIGHT_EDGE, addh+ROW_HEIGHT)
                
                right_txt = RIGHT_EDGE
                dindex = 0
                for data in row:
                    right_txt -= MARGIN+LINE
                    if dindex == 2 or dindex == 3:
                        fontsize = 8
                        fdesc.set_size(fontsize * pango.SCALE)
                        self.pangolayout.set_font_description(fdesc)
                        self.pangolayout.set_text(data)
                        (width, height) = self.pangolayout.get_size()
                        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
                        cr.move_to (right_txt -(width / pango.SCALE), addh + (ROW_HEIGHT-(height / pango.SCALE))/2)
                        self.pangocairo.show_layout(self.pangolayout)
                        fontsize = 9
                        fdesc.set_size(fontsize * pango.SCALE)
                        self.pangolayout.set_font_description(fdesc)
                    else:
                        self.pangolayout.set_text(data)
                        (width, height) = self.pangolayout.get_size()
                        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
                        cr.move_to (right_txt -(width / pango.SCALE), addh + (ROW_HEIGHT-(height / pango.SCALE))/2)
                        self.pangocairo.show_layout(self.pangolayout)
                
                    right_txt -= self.cols_width[dindex]
                    cr.move_to(right_txt, addh)
                    cr.line_to(right_txt, addh + ROW_HEIGHT)
                    
                    dindex += 1
                    
                self.debt_sum += int(row[4].replace(",", ""))
                self.credit_sum += int(row[5].replace(",", ""))
                
                addh += ROW_HEIGHT
                offset += 1
        except IndexError:
            pass
        
        right_txt = RIGHT_EDGE
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)
        
        right_txt -= 4*(MARGIN + LINE) + self.cols_width[0] + self.cols_width[1] + self.cols_width[2]
        self.pangolayout.set_text(_("Sum"))
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        cr.move_to (right_txt -(width / pango.SCALE), addh + (ROW_HEIGHT-(height / pango.SCALE))/2)
        self.pangocairo.show_layout(self.pangolayout)    
        right_txt -= self.cols_width[3]
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)
        
        cr.move_to(RIGHT_EDGE, addh)
        cr.line_to(right_txt, addh)
        
        right_txt -= MARGIN + LINE
        self.pangolayout.set_text(utility.showNumber(self.debt_sum))
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        cr.move_to (right_txt -(width / pango.SCALE), addh + (ROW_HEIGHT-(height / pango.SCALE))/2)
        self.pangocairo.show_layout(self.pangolayout)    
        right_txt -= self.cols_width[4]
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)
        
        right_txt -= MARGIN + LINE
        self.pangolayout.set_text(utility.showNumber(self.credit_sum))
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        cr.move_to (right_txt -(width / pango.SCALE), addh + (ROW_HEIGHT-(height / pango.SCALE))/2)
        self.pangocairo.show_layout(self.pangolayout)    
        right_txt -= self.cols_width[5]
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)
        
        cr.move_to(self.page_margin, addh + ROW_HEIGHT)
        cr.line_to(RIGHT_EDGE, addh + ROW_HEIGHT)
            
        cr.stroke()
        
    def setDrawFunction(self, func):
        self.drawfunction = func

    def drawTableHeading(self):
        RIGHT_EDGE = 570  #(table width + PAGE_MARGIN)
        HEADING_HEIGHT = self.heading_height
        MARGIN = self.cell_margin
        LINE = self.line
        
        cr = self.cairo_context
        
        htop = self.header_height + self.page_margin
        #Heading top line
        cr.move_to(self.page_margin, htop)
        cr.line_to(RIGHT_EDGE, htop)
        
        cr.move_to(RIGHT_EDGE, htop)
        cr.line_to(RIGHT_EDGE, htop + HEADING_HEIGHT)
        
        #Draw table headings
        right_txt = RIGHT_EDGE
        dindex = 0
        for data in self.heading:
            right_txt -= MARGIN+LINE
            self.pangolayout.set_text(data)
            (width, height) = self.pangolayout.get_size()
            if (width / pango.SCALE) > self.cols_width[dindex]:
                res = data.split()
                self.pangolayout.set_text(res[0])
                (width, height) = self.pangolayout.get_size()
                if (width / pango.SCALE) < self.cols_width[dindex]:
                    #self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
                    cr.move_to (right_txt -(width / pango.SCALE), htop + (HEADING_HEIGHT/2-(height / pango.SCALE))/2)
                    self.pangocairo.show_layout(self.pangolayout)
                    #
                    self.pangolayout.set_text(res[1])
                    (width, height) = self.pangolayout.get_size()
                    #self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
                    cr.move_to (right_txt -(width / pango.SCALE), htop + ((HEADING_HEIGHT*3)/2-(height / pango.SCALE))/2)
                    self.pangocairo.show_layout(self.pangolayout)                    
            else:
                #self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
                cr.move_to (right_txt -(width / pango.SCALE), htop + (HEADING_HEIGHT-(height / pango.SCALE))/2)
                self.pangocairo.show_layout(self.pangolayout)
        
            right_txt -= self.cols_width[dindex]
            cr.move_to(right_txt, htop)
            cr.line_to(right_txt, htop + HEADING_HEIGHT)
            
            dindex += 1

#    def dailySpecific(self, pos, page):
#        right_txt = 570
#        MARGIN = self.cell_margin
#        LINE = self.line
#        ROW_HEIGHT = self.row_height
#        TABLE_TOP = self.header_height + self.heading_height + self.page_margin
#        cr = self.cairo_context
#        
#        row_nr = page * self.lines_per_page + pos
#        try:
#            self.debt_sum += int(self.content[row_nr-1][4].replace(",", ""))
#            self.credit_sum += int(self.content[row_nr-1][5].replace(",", ""))
#        except AttributeError:
#            self.debt_sum = int(self.content[row_nr-1][4].replace(",", ""))
#            self.credit_sum = int(self.content[row_nr-1][5].replace(",", ""))
#           
#        if pos == 1 or pos == self.lines_per_page or row_nr == len(self.content):
#            if pos != 1:
#                TABLE_TOP += (pos + 1) * ROW_HEIGHT
#                cr.move_to(self.page_margin, TABLE_TOP + ROW_HEIGHT)
#                cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
#                
#            cr.move_to(right_txt, TABLE_TOP)
#            cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
#            
#            self.pangolayout.set_text("----")
#            (width, height) = self.pangolayout.get_size()
#            self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
#            
#            for i in range(0, 3):
#                right_txt -= MARGIN + LINE
#                cr.move_to (right_txt -(width / pango.SCALE), TABLE_TOP + (ROW_HEIGHT-(height / pango.SCALE))/2)
#                self.pangocairo.show_layout(self.pangolayout)    
#                right_txt -= self.cols_width[i]
#                cr.move_to(right_txt, TABLE_TOP)
#                cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
#            
#            right_txt -= MARGIN + LINE
#            if pos == 1:
#                self.pangolayout.set_text(_("Sum of previous page"))
#            else:
#                self.pangolayout.set_text(_("Sum"))    
#                
#            (width, height) = self.pangolayout.get_size()
#            self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
#            cr.move_to (right_txt -(width / pango.SCALE), TABLE_TOP + (ROW_HEIGHT-(height / pango.SCALE))/2)
#            self.pangocairo.show_layout(self.pangolayout)    
#            right_txt -= self.cols_width[3]
#            cr.move_to(right_txt, TABLE_TOP)
#            cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
#            
#            right_txt -= MARGIN + LINE
#            if page == 0 and pos == 1:
#                self.pangolayout.set_text("0")
#            else:
#                self.pangolayout.set_text(utility.showNumber(self.debt_sum))
#            (width, height) = self.pangolayout.get_size()
#            self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
#            cr.move_to (right_txt -(width / pango.SCALE), TABLE_TOP + (ROW_HEIGHT-(height / pango.SCALE))/2)
#            self.pangocairo.show_layout(self.pangolayout)    
#            right_txt -= self.cols_width[4]
#            cr.move_to(right_txt, TABLE_TOP)
#            cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
#            
#            right_txt -= MARGIN + LINE
#            if page == 0 and pos == 1:
#                self.pangolayout.set_text("0")
#            else:
#                self.pangolayout.set_text(utility.showNumber(self.credit_sum))
#            (width, height) = self.pangolayout.get_size()
#            self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
#            cr.move_to (right_txt -(width / pango.SCALE), TABLE_TOP + (ROW_HEIGHT-(height / pango.SCALE))/2)
#            self.pangocairo.show_layout(self.pangolayout)    
#            right_txt -= self.cols_width[5]
#            cr.move_to(right_txt, TABLE_TOP)
#            cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
    
    def subjectSpecific(self, pos, page):
        pass
        
    def docSpecific(self, pos, page):
        pass
            
    