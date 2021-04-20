from building_blocks import *

class SweepParam():

    def __init__(self,params):

        if isinstance(params,dict):

            self._dict=params

        else:
            # import pdb; pdb.set_trace()
            raise ValueError("SweepParam is init by dict of names:values")

    def __call__(self):

        return self._dict

    def __len__(self):
        return len(self._dict[list(self._dict.keys())[0]])

    def __repr__(self):

        return str(self._dict)

    @property
    def names(self):

        return [x for x in self._dict.keys()]

    @property
    def values(self):

        return [_ for _ in self._dict.values()]

    def combine(self,sweep2):

        sweep1=self

        if not isinstance(sweep2,SweepParam):

            raise ValueError("the parameter needs to be a SweepParam")

        init_names=sweep1.names

        new_names=sweep2.names

        init_values=[]

        for x in sweep1.values:

            if isinstance(x,np.ndarray):

                init_values.append(x.tolist())

            else:

                init_values.append(x)

        new_values=[]

        for x in sweep2.values:

            if isinstance(x,np.ndarray):

                new_values.append(x.tolist())

            else:

                new_values.append(x)

        if any([name in new_names for name in init_names]):

            raise ValueError("Unexpected behaviour:at least one sweep parameter is repeated")


        if len(init_values)>1:

            init_values=[_ for _ in zip(*init_values)]

        else:

            init_values=init_values[0]

        if len(new_values)>1:

            new_values=[_ for _ in zip(*new_values)]

        else:

            new_values=new_values[0]

        import itertools

        tot_values=[_ for _ in itertools.product(init_values,new_values)]

        new_length=len(tot_values)

        def flatten(L):
            for item in L:
                try:
                    yield from flatten(item)
                except TypeError:
                    yield item

        tot_values=[_ for _ in flatten(tot_values)]

        # import pdb; pdb.set_trace()

        dict_new={x : [] for x in init_names+new_names}

        # import pdb; pdb.set_trace()

        for index in range(new_length):

            for name in dict_new.keys():

                dict_new[name].append(tot_values.pop(0))

            # print(dict_new)

        return SweepParam(dict_new)

class _SweepParamValidator():

    def __init__(self,def_param=ld.Arrayx_param):

        self.default_value=SweepParam(def_param)

    def __set_name__(self,obj,name):

        self.private_name="_"+name

    def __get__(self,obj,objtype=None):

        if not hasattr(obj,self.private_name):

            return self.default_value

        else:

            return getattr(obj,self.private_name)

    def __set__(self,obj,layout_param):

        if not isinstance(obj, LayoutPart):

            raise ValueError("{} needs to derive from LayoutPart".format(obj))

        else:

            if not isinstance(layout_param,SweepParam):

                raise ValueError("param needs to be a SweepParam")

            self._set_valid_names(obj.get_params_name())

            if not all([names in self._valid_names for names in layout_param.names]):

                raise ValueError("At least one param key is invalid")

            else:

                it = iter(layout_param.values)

                the_len = len(next(it))

                if not all(len(x)==the_len for x in it):

                    raise ValueError("All params need to have same length")

                else:

                    setattr(obj,self.private_name,layout_param)

    def _set_valid_names(self,opts):

        if isinstance(opts, str):

            opts=list(opts)

        self._valid_names=opts

class ParametricArray(LayoutPart):

    x_param=_SweepParamValidator(ld.Arrayx_param)

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)
        self.device=IDT(self.name)
        self.x_spacing=ld.Arrayx_spacing
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

        param=self.x_param

        for index in range(len(param)):

            for name,value in zip(param.names,param.values):

                df[name]=value[index]

            device.import_params(df)

            print("drawing device {} of {}".format(index+1,len(param)))

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

        g.distribute(spacing=self.x_spacing)

        g.align(alignment='ymin')

        del device, cells ,g

        return master_cell

    def auto_labels(self,top=True,bottom=True,top_label=None,bottom_label=None,\
        col_index=0,row_index=0):

        param=self.x_param

        l=len(param)

        sweep_label=[]

        for name in param.names:

            sweep_label.append(''.join([c for c in name if c.isupper()]))

        top_label_sweep=[]

        for i in range(l):

            for lab in sweep_label:

                tmp_lab=' '.join([x+str(i) for x in sweep_label])

            top_label_sweep.append(tmp_lab)

        if top_label is None:

            top_label=top_label_sweep

        else:

            top_label=[ top_label+" "+ x for x in top_label_sweep]

        if bottom_label is None:

            bottom_label=""

        else:

            bottom_label=bottom_label+" "

        bottom_label=[bottom_label+"{:03d} x {:03}".format(col_index,y) for y in range(row_index,row_index+l)]

        if top==True:

            self.labels_top=top_label

        else:

            self.labels_top=None

        if bottom==True:

            self.labels_bottom=bottom_label

        else:

            self.labels_bottom=None

class ParametricMatrix(ParametricArray):

    y_param=_SweepParamValidator(ld.Matrixy_param)

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.y_spacing=ld.Matrixy_spacing
        self.labels_top=ld.Matrixlabels_top
        self.labels_bottom=ld.Matrixlabels_bottom

    def draw(self,layer=None,*args,**kwargs):

        original_device=deepcopy(self.device)

        device=self.device

        df=device.export_params()

        master_cell=Device(name=self.name)

        cells=list()

        top_label_matrix=self.labels_top

        bottom_label_matrix=self.labels_bottom

        y_param=self.y_param

        for index in range(len(y_param)):

            for name,value in zip(y_param.names,y_param.values):

                df[name]=value[index]

            device.import_params(df)

            print("drawing array {} of {}".format(index+1,len(y_param)))

            if top_label_matrix is not None:

                if isinstance(top_label_matrix[index],list):

                    if len(top_label_matrix[index])==len(self.x_param):

                        self.labels_top=top_label_matrix[index]

                    else:

                        self.labels_top=None

                else:

                    self.labels_top=None

            if bottom_label_matrix is not None:

                if isinstance(bottom_label_matrix[index],list):

                    if len(bottom_label_matrix[index])==len(self.x_param):

                        self.labels_bottom=bottom_label_matrix[index]

                    else:

                        self.labels_bottom=None

                else:

                    self.labels_bottom=None

            new_cell=ParametricArray.draw(self,layer,*args,**kwargs)

            new_cell.name=self.name+str(index)

            master_cell<<new_cell

            cells.append(new_cell)

        g=Group(cells)

        g.distribute(direction='y',spacing=self.y_spacing)

        g.align(alignment='xmin')

        del device, cells ,g

        self.device=original_device

        self.cell=master_cell

        return master_cell

    def auto_labels(self,top=True,bottom=True,top_label=None,bottom_label=None,\
        col_index=0,row_index=0):

        l=len(self.y_param)

        top_label_matrix=[]

        bottom_label_matrix=[]

        row_label_sweep=[]

        for name in self.y_param.names:

            row_label_sweep.append(''.join([c for c in name if c.isupper() ]))

        for i in range(l):

            row_lab=' '.join([x+str(i) for x in row_label_sweep])

            ParametricArray.auto_labels(self,top_label=row_lab,bottom_label=bottom_label,\
                col_index=i+col_index,row_index=row_index)

            top_label_matrix.append(self.labels_top)

            bottom_label_matrix.append(self.labels_bottom)

        if top==True:

            self.labels_top=top_label_matrix

        else:

            self.labels_top=None

        if bottom==True:

            self.labels_bottom=bottom_label_matrix

        else:

            self.labels_bottom=None
