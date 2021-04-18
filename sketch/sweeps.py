
from building_blocks import *

class _LayoutParam():

    def __init__(self,pars):

        self.default_value=pars

    def __set_name__(self,obj,name):

        self.private_name="_"+name

    def __get__(self,obj,objtype=None):

        if not hasattr(obj,self.private_name):

            return self.default_value

        else:

            return getattr(obj,self.private_name)

    def __set__(self,obj,value):

        if not isinstance(obj, LayoutPart):

            raise ValueError("{} needs to derive from LayoutPart".format(obj))

        else:

            self._set_valid_names(obj.get_params_name())

            if not isinstance(value,dict):

                raise ValueError("{} needs to be a dict".format(value))

            else:

                if not all([names in self._valid_names for names in value.keys()]):

                    raise ValueError("At least one param key is invalid")

                else:

                    it = iter(value.values())

                    the_len = len(next(it))

                    if not all(len(x)==the_len for x in it):

                        raise ValueError("All params need to have same length")

                    else:

                        setattr(obj,self.private_name,value)

    def _set_valid_names(self,opts):

        if isinstance(opts, str):

            opts=list(opts)

        self._valid_names=opts

class ParametricArray(LayoutPart):

    param=_LayoutParam(ld.Arrayparam)

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)
        self.device=IDT(self.name)
        self.spacing=ld.Arrayspacing
        self.labels_top=ld.Arraylabels_top
        self.labels_bottom=ld.Arraylabels_bottom

    @property
    def device(self):

        return self._device

    @device.setter
    def device(self,value):

        from building_blocks import LayoutPart

        if not isinstance(value,LayoutPart):

            raise Exception("{} is an invalid entry for object of {}".format(value,self.device.__class__.__name__))

        else:

            self._device=value

            self._device.name=self.name

    def export_params(self):

        df=self.device.export_params()
        # warnings.warn("ParamArray.export_params() returned from device")
        return df

    def import_params(self,df):

        self.device.import_params(df)
        # warnings.warn("ParamArray.import_params() passed to device")

    def draw(self,layer=None,*args,**kwargs):

        device=copy(self.device)

        df=device.export_params()

        master_cell=Device(name=self.name)

        cells=list()

        param=self.param

        for index in range(len(self)):

            # import pdb; pdb.set_trace()

            for name,value in param.items():

                df[name]=value[index]

            device.import_params(df)

            new_cell=device.draw()

            if self.labels_top is not None or self.labels_bottom is not None:

                if layer is None:

                    if hasattr(device,'probe'):

                        layer=device.probe.layer

                    elif hasattr(device,'layer'):

                        layer=device.layer

                    else:

                            raise Exception ("Specify Text Layer")

                if self.labels_top is not None:

                    device.add_text(layer=layer,location='top',\
                    text=self.labels_top[index],*args,**kwargs)

                if self.labels_bottom is not None:

                    device.add_text(layer=layer,location='bottom',\
                    text=self.labels_bottom[index],*args,**kwargs)

            master_cell<<new_cell

            cells.append(new_cell)

        g=Group(cells)

        g.distribute(spacing=self.spacing)

        del device, cells ,g

        return master_cell

    def __len__(self):

        return len(self.param[list(self.param.keys())[0]])

    def gen_labels(self,top=True,bottom=True,top_label=None,bottom_label=None,\
        col_index=0,row_index=0):

        l=len(self)

        if top_label is None:

            top_label=[]

            sweep_label=[]

            for name in self.param.keys():

                sweep_label.append(''.join([c for c in name if c.isupper() and not c in {'I','D','T'}]))

            for i in range(1,l+1):

                for lab in sweep_label:

                    tmp_lab=' '.join([x+str(i) for x in sweep_label])

                top_label.append(tmp_lab)

        else:

            top_label=[top_label+x for x in range(1,l+1)]

        if bottom_label is None:

            bottom_label=""

        bottom_label=[bottom_label+"{:03d} x {:03}".format(col_index,y) for y in range(row_index,row_index+l+1)]

        if top==True:

            self.labels_top=top_label

        else:

            self.labels_top=None

        if bottom==True:

            self.labels_bottom=bottom_label

        else:

            self.labels_bottom=None
