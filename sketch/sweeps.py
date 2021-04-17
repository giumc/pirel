from building_blocks import *

class ParametricArray(LayoutPart):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)
        self.device=IDT(self.name)
        self.spacing=ld.Arrayspacing
        self.param_name=ld.Arrayparam_name
        self.param_value=ld.Arrayparam_value
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

    @property
    def param_name(self):

        if not all( [names in self.get_available_params() for names in self._param_name]):
            # import pdb; pdb.set_trace()
            raise Exception("Cannot continue as param_name is invalid")

        else:

            return self._param_name

    @param_name.setter
    def param_name(self,name):

        if isinstance(name,str):

            name=[name]

        if not all([names in self.get_available_params() for names in name]) :
            print(*self.get_available_params())
            raise Exception("{}\n".format("Bad entries for param_name property"))

        else:

            self._param_name= name

    @property
    def param_value(self):

            return self._param_value

    @param_value.setter
    def param_value(self,value):

        import numpy as np

        if not isinstance(value,np.ndarray):

            value=np.array(value)

        self._param_value=value

    def get_available_params(self):

        return self.device.export_params().columns

    def export_params(self):

        df=self.device.export_params()
        warnings.warn("ParamArray.export_params() returned from device")
        return df

    def import_params(self,df):

        self.device.import_params(df)
        warnings.warn("ParamArray.import_params() passed to device")

    def draw(self,text_size=25,text_font="BebasNeue-Regular.otf",text_layer=None):

        device=copy(self.device)

        df=device.export_params()

        param_name=self.param_name

        param_value=self.param_value

        if param_value.ndim>1:

            n_cells = param_value.shape[1]

        else:

            n_cells = len(param_value)

        master_cell=Device(name=self.name)

        cells=list()

        for i_val in range(n_cells):

            # import pdb ; pdb.set_trace()

            if param_value.ndim>1:

                for i_name,name in enumerate(param_name):

                    df[name]=param_value[i_name,i_val]

            else:

                df[param_name]=param_value[i_val]

            device.import_params(df)

            new_cell=device.draw()

            if self.labels_top is not None or self.labels_bottom is not None:

                if text_layer is None:

                    if hasattr(device,'probe'):

                        text_layer=device.probe.layer

                    elif hasattr(device,'layer'):

                        text_layer=device.layer

                    else:

                            raise Exception ("Specify Text Layer")

                if self.labels_top is not None:

                    device.add_text(text=self.labels_top[i_val],location='top',\
                        size=text_size,font=text_font,\
                        layer=text_layer)

                if self.labels_bottom is not None:

                    device.add_text(text=self.labels_bottom[i_val],location='bottom',\
                        size=text_size,font=text_font,\
                        layer=text_layer)

            master_cell<<new_cell

            cells.append(new_cell)

        g=Group(cells)

        g.distribute(spacing=self.spacing)

        del device, cells ,g

        return master_cell

class ParametricMatrix(LayoutPart):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.device=DUT()
