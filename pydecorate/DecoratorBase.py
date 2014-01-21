# pydecorate - python module for labelling 
# and adding colour scales to images
# 
#Copyright (C) 2011  Hrobjartur Thorsteinsson
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

try:
    from PIL import Image, ImageFont
except ImportError:
    print "ImportError: Missing PIL image objects"

try:
    import ImageDraw
except ImportError:
    print "ImportError: Missing module: ImageDraw"

# style dictionary defines default options
# some only used by aggdraw version of the decorator
default_style_dict = {
'cursor':[0,0],
'margins':[5,5],
'height':60,
'width':60,
'propagation':[1,0],
'newline_propagation':[0,1],
'alignment':[0.0,0.0],
'bg':'white',
'bg_opacity':127,
'line':"black",
'line_width':1,
'line_opacity':255,
'outline':None,
'outline_width':1,
'outline_opacity':255,
'fill':'black',
'fill_opacity':255,
'font':None,
'start_border':[0,0],
'extend':False,
'tick_marks':1.0,
'minor_tick_marks':0.1
}

class DecoratorBase(object):
    def __init__(self,image):
        """
        Probably users only want to instantiate DecoratorAgg or the Decorator implementations.
        DecoratorBase is a base class outlining common operations and interface for the Decorator (PIL drawing engine) and DecoratorAgg (Aggdraw drawing engine)
        """
        self.image = image
        
        import copy
        self.style = copy.deepcopy(default_style_dict)

    def set_style(self, **kwargs):
        self.style.update(kwargs)
        self.style['cursor'] = list(self.style['cursor'])

    def _finalize(self, draw):
        """Do any need finalization of the drawing
        """
        pass

    def write_vertically(self):
        # top-right
        if self.style['alignment'][0] == 1.0 and self.style['alignment'][1] == 0.0:
            self.style['propagation']=[0,1]
            self.style['newline_propagation']=[-1,0]
        # bottom-right 
        elif self.style['alignment'][0] == 1.0 and self.style['alignment'][1] == 1.0:
            self.style['propagation']=[0,-1]
            self.style['newline_propagation']=[-1,0]
        # bottom-left
        elif self.style['alignment'][0] == 0.0 and self.style['alignment'][1] == 1.0:
            self.style['propagation']=[0,-1]
            self.style['newline_propagation']=[1,0]
        # top-left and other alignments
        else:
            self.style['propagation']=[0,1]
            self.style['newline_propagation']=[1,0]

    def write_horizontally(self):
        # top-right
        if self.style['alignment'][0] == 1.0 and self.style['alignment'][1] == 0.0:
            self.style['propagation']=[-1,0]
            self.style['newline_propagation']=[0,1]
        # bottom-right 
        elif self.style['alignment'][0] == 1.0 and self.style['alignment'][1] == 1.0:
            self.style['propagation']=[-1,0]
            self.style['newline_propagation']=[0,-1]
        # bottom-left
        elif self.style['alignment'][0] == 0.0 and self.style['alignment'][1] == 1.0:
            self.style['propagation']=[1,0]
            self.style['newline_propagation']=[0,-1]
        # top-left and other alignments
        else:
            self.style['propagation']=[1,0]
            self.style['newline_propagation']=[0,1]

    def align_bottom(self):
        if self.style['alignment'][1] != 1.0:
            self.style['alignment'][1] = 1.0
            self.style['newline_propagation'][1] = -self.style['newline_propagation'][1]
            self.style['propagation'][1] = -self.style['propagation'][1]
            self.home()

    def align_top(self):
        if self.style['alignment'][1] != 0.0:
            self.style['alignment'][1] = 0.0
            self.style['newline_propagation'][1] = -self.style['newline_propagation'][1]
            self.style['propagation'][1] = -self.style['propagation'][1]
            self.home()

    def align_right(self):
        if self.style['alignment'][0] != 1.0:
            self.style['alignment'][0] = 1.0
            self.style['propagation'][0] = -self.style['propagation'][0]
            self.style['newline_propagation'][0] = -self.style['newline_propagation'][0]
            self.home()

    def align_left(self):
        if self.style['alignment'][0] != 0.0:
            self.style['alignment'][0] = 0.0
            self.style['propagation'][0] = -self.style['propagation'][0]
            self.style['newline_propagation'][0] = -self.style['newline_propagation'][0]
            self.home()

    def home(self):
        self.style['cursor'][0] = int( self.style['alignment'][0] * self.image.size[0] )
        self.style['cursor'][1] = int( self.style['alignment'][1] * self.image.size[1] )

    def rewind(self):
        if self.style['newline_propagation'][0] == 0:
            self.style['cursor'][0] = int( self.style['alignment'][0] * self.image.size[0] )
        if self.style['newline_propagation'][1] == 0:
            self.style['cursor'][1] = int( self.style['alignment'][1] * self.image.size[1] )

    def new_line(self):
        # set new line
        self.style['cursor'][0] += self.style['newline_propagation'][0] * self.style['width']
        self.style['cursor'][1] += self.style['newline_propagation'][1] * self.style['height']
        # rewind
        self.rewind()

    def _step_cursor(self):
        self.style['cursor'][0] += self.style['propagation'][0] * self.style['width']
        self.style['cursor'][1] += self.style['propagation'][1] * self.style['height']

    #def start_border(self):
    #    self.style['start_border'] = list( self.style['cursor'] )
    #    
    #def end_border(self,**kwargs):
    #    x0=self._start_border[0]
    #    y0=self._start_border[1]
    #    x1=self._cursor[0]
    #    y1=self._cursor[1]+self._line_size[1]
    #    draw=self._get_canvas(self.image)
    #    self._add_rectangle(draw,[x0,y0,x1,y1],bg=None,**kwargs)
    #    self._finalize(draw)

    def _add_polygon(self,draw,xys,**kwargs):
        draw.polygon(xys,fill=kwargs['fill'],outline=kwargs['outline'])

    def _get_canvas(self, img):
        raise NotImplementedError("Derived class implements this.")

    def _load_default_font(self):
        raise NotImplementedError("Derived class implements this.")

    def _add_text(self,txt,**kwargs): 
        # synchronize kwargs into style
        self.set_style(**kwargs)

        # draw object
        draw = self._get_canvas(self.image)

        # check for font object
        if self.style['font'] is None: 
            self.style['font'] = self._load_default_font()

        # image size
        x_size, y_size = self.image.size

        # split text into newlines '\n'
        txt_nl=txt.split('\n')

        # current xy and margins
        x = self.style['cursor'][0]
        y = self.style['cursor'][1]
        mx = self.style['margins'][0]
        my = self.style['margins'][1]
        prev_width  = self.style['width']
        prev_height = self.style['height']

        # calculate text space
        tw,th = draw.textsize(txt_nl[0],self.style['font'])
        for t in txt_nl:
            w,tmp = draw.textsize(t,self.style['font'])
            if w > tw: tw = w
        hh=len(txt_nl)*th

        # set height/width for subsequent draw operations
        if prev_height < int(hh+2*my): 
            self.style['height'] = int(hh+2*my)
        self.style['width'] = int(tw+2*mx)

        # draw base
        px = (self.style['propagation'][0] + self.style['newline_propagation'][0])
        py = (self.style['propagation'][1] + self.style['newline_propagation'][1])
        x1 = x + px*(tw + 2*mx)
        y1 = y + py*self.style['height']
        self._add_rectangle(draw,[x,y,x1,y1],**self.style)
        
        # draw
        for i in range(len(txt_nl)):
            pos_x = x + mx
            pos_y = y + i*th+my
            if py < 0:
                pos_y += py*self.style['height']
            if px < 0:
                pos_x += px*self.style['width']
            self._add_text_line(draw,(pos_x,pos_y),txt_nl[i], self.style['font'], fill=self.style['fill'])

        # update cursor
        self._step_cursor()

        # finalize
        self._finalize(draw)

    def _add_text_line(self,draw,xy,text,font,fill='black'):
        draw.text(xy,text, font=font, fill=fill)
        
    def _add_line(self,draw,xys,**kwargs):
        draw.line(xys,fill=kwargs['line']) # inconvenient to use fill for a line so swapped def.

    def _add_rectangle(self,draw,xys,**kwargs):
        # adjust extent of rectangle to draw up to but not including xys[2/3]
        xys[2]-=1
        xys[3]-=1
        if kwargs['bg'] or kwargs['outline']:
            draw.rectangle(xys,fill=kwargs['bg'],outline=kwargs['outline'])

    def _add_logo(self, logo_path, **kwargs):
        # synchronize kwargs into style
        self.set_style(**kwargs)

        # current xy and margins
        x=self.style['cursor'][0]
        y=self.style['cursor'][1]

        mx=self.style['margins'][0]
        my=self.style['margins'][1]

        # draw object
        draw = self._get_canvas(self.image)

        # get logo image
        logo=Image.open(logo_path,"r").convert('RGBA')
        
        # default size is _line_size set by previous draw operation
        # else do not resize
        nx,ny=logo.size
        aspect=float(ny)/nx
        
        # default logo sizes ...
        # use previously set line_size
        if self.style['propagation'][0] != 0:
            ny = self.style['height'] 
            nyi = int(round(ny-2*my))
            nxi = int(round(nyi/aspect))
            nx = (nxi + 2*mx)
        elif self.style['propagation'][1] != 0:
            nx = self.style['width']
            nxi = int(round(nx-2*mx))
            nyi = int(round(nxi*aspect))
            ny = (nyi + 2*my)

        logo = logo.resize((nxi,nyi),resample=Image.ANTIALIAS)
        
        # draw base
        px = (self.style['propagation'][0] + self.style['newline_propagation'][0])
        py = (self.style['propagation'][1] + self.style['newline_propagation'][1])
        box = [x, y, x+px*nx, y+py*ny]
        self._add_rectangle(draw,box,**self.style)

        #finalize
        self._finalize(draw)

        # paste logo
        box = [x+px*mx, y+py*my, x+px*mx+px*nxi, y+py*my+py*nyi]
        self._insert_RGBA_image(logo,box)
 
        # update cursor
        self.style['width'] = int(nx)
        self.style['height'] = int(ny)
        self._step_cursor()

    def _add_scale(self, colormap, **kwargs):
        # synchronize kwargs into style
        self.set_style(**kwargs)

        # sizes, current xy and margins
        x=self.style['cursor'][0]
        y=self.style['cursor'][1]
        mx=self.style['margins'][0]
        my=self.style['margins'][1]
        x_size,y_size = self.image.size

        # horizontal/vertical?
        is_vertical = False
        if self.style['propagation'][1] != 0:
            is_vertical = True
        
        # adjust new size based on extend (fill space) style,
        if self.style['extend']:
            if self.style['propagation'][0] == 1:
                self.style['width'] = (x_size - x)
            elif self.style['propagation'][0] == -1:
                self.style['width'] = x
            if self.style['propagation'][1] == 1:
                self.style['height'] = (y_size - y)
            elif self.style['propagation'][1] == -1:
                self.style['height'] = y

        # draw object
        draw = self._get_canvas(self.image)
        
        # draw base
        px = (self.style['propagation'][0] + self.style['newline_propagation'][0])
        py = (self.style['propagation'][1] + self.style['newline_propagation'][1])
        x1 = x + px*self.style['width']
        y1 = y + py*self.style['height']
        self._add_rectangle(draw,[x,y,x1,y1],**self.style)

        # scale dimensions
        scale_width = self.style['width'] - 2*mx
        scale_height = self.style['height'] - 2*my
        
        # generate color scale image obj inset by margin size mx my,
        import numpy as np
        from trollimage.image import Image as TImage
        
        #### THIS PART TO BE INGESTED INTO A COLORMAP FUNCTION ####
        minval,maxval = colormap.values[0],colormap.values[-1]
        
        if is_vertical:
            linedata = np.ones((scale_width,1)) * np.arange(minval,maxval,(maxval-minval)/scale_height)
            linedata = linedata.transpose()
        else:
            linedata = np.ones((scale_height,1)) * np.arange(minval,maxval,(maxval-minval)/scale_width)

        timg = TImage(linedata,mode="L")
        timg.colorize(colormap)
        scale = timg.pil_image()
        ###########################################################

        # finalize (must be before paste)
        self._finalize(draw)

        # paste scale onto image
        pos =(min(x,x1)+mx,min(y,y1)+my)
        self.image.paste(scale,pos)

        # reload draw object
        draw = self._get_canvas(self.image)

        # draw tick marks
        #x_steps = np.arange(x+mx, x+mx+scale_width, scale_width/((maxval-minval)/self.style['tick_marks']))
        #for xs in x_steps:
        #    print xs
        #    self._add_line(draw,[(xs,y+mx),(xs,y+scale_height/2.0)],**self.style)
        
                

        # finalize
        self._finalize(draw)

    def _form_xy_box(self,box):
        newbox = box + []
        if box[0] > box[2]:
            newbox[0] = box[2]
            newbox[2] = box[0]
        if box[1] > box[3]:
            newbox[1] = box[3]
            newbox[3] = box[1]
        return newbox

    def _insert_RGBA_image(self,img,box):
        # make sure box is formed tl to br corners:
        box = self._form_xy_box(box)
        # crop area for compositing
        crop=self.image.crop(box)
        comp=Image.composite(img,crop,img)
        self.image.paste(comp,box)
