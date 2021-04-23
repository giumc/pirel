from building_blocks import *

class SweepParam():

    def __init__(self,params):

        if isinstance(params,dict):

            self._dict=params

        else:
            # import pdb; pdb.set_trace()
            raise ValueError("SweepParam is init by dict of names:values")

    def __call__(self,*args):

        if not args:

            return self._dict

        elif isinstance(args[0],int):

            return {x:y[args[0]] for x,y in zip(self.names,self.values)}

    def __len__(self):
        return len(self._dict[list(self._dict.keys())[0]])

    def __repr__(self):

        return str(self._dict)

    @property
    def labels(self):

        param=self

        l=len(param)

        sweep_label=[]

        for name in param.names:

            sweep_label.append(''.join([c for c in name if c.isupper()]))

        stringout=[]

        # import pdb; pdb.set_trace()

        unique={name:list(dict.fromkeys(values)) for name,values in zip(param.names,param.values)}

        for i in range(l):

            # print(i)

            tmp_lab=''

            for lab,name in zip(sweep_label,param.names):

                # import pdb; pdb.set_trace()

                tmp_lab=tmp_lab+" " +lab+str(unique[name].index(param()[name][i]))

                # print(tmp_lab)

            stringout.append(tmp_lab)

        return stringout

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

                import pdb; pdb.set_trace()

                raise ValueError("At least one param key in {} is invalid".format(*layout_param.names))

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

        try:

            if isinstance(args[0],LayoutPart):

                self.device=args[0]

        except Exception:

            self.device=IDT(name="Hello")

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

        return self.device.export_params()

    @property
    def table(self):

        param=self.x_param

        device=deepcopy(self.device)

        data_tot=DataFrame()

        for i in range(len(param)):

            for name in param.names:

                device.import_params(DataFrame(param(i),index=[0]))

            df=device.export_params()

            if self.labels_bottom is not None:

                df.index=[self.labels_bottom[i]]

            else:

                df.index=[i]

            data_tot=data_tot.append(df)

        return data_tot

    def import_params(self,df):

        self.device.import_params(df)
        # warnings.warn("ParamArray.import_params() passed to device")

    def draw(self):

        device=deepcopy(self.device)

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

            if self.labels_top is not None:

                self.add_text(new_cell,\
                text_opts=self.text_params.update({\
                    'location':'top','label':self.labels_top[index]}))

            if self.labels_bottom is not None:

                self.add_text(new_cell,\
                text_opts=self.text_params.update({\
                    'location':'bottom','label':self.labels_bottom[index]}))

            master_cell<<new_cell

            cells.append(new_cell)

        g=Group(cells)

        g.distribute(spacing=self.x_spacing)

        g.align(alignment='ymin')

        del device, cells ,g

        # master_cell.flatten()

        master_cell=join(master_cell)

        self.cell=master_cell

        return master_cell

    def auto_labels(self,top=True,bottom=True,top_label='',bottom_label='',\
        col_index=0,row_index=0):

        param=self.x_param

        top_label=[top_label+" "+ x for x in param.labels]

        bottom_label=[bottom_label+"{:03d} x {:03d}".format(col_index,y) for y in range(row_index,row_index+len(param))]

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

    def draw(self):

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

            new_cell=ParametricArray.draw(self)

            new_cell.name=self.name+str(index)

            master_cell<<new_cell

            cells.append(new_cell)

        g=Group(cells)

        g.distribute(direction='y',spacing=self.y_spacing)

        g.align(alignment='xmin')

        del device, cells ,g

        self.device=original_device

        master_cell.flatten()

        master_cell=join(master_cell)

        self.device=original_device

        self.cell=master_cell

        self.labels_top=top_label_matrix

        self.labels_bottom=bottom_label_matrix

        return master_cell

    def auto_labels(self,top=True,bottom=True,top_label='',bottom_label='',\
        col_index=0,row_index=0):

        # import pdb; pdb.set_trace()

        y_label=[top_label+x for x  in self.y_param.labels]

        x_label=[top_label+x for x in self.x_param.labels]

        import itertools

        top_label=[[top_label+x+y for x in x_label] for y in y_label]

        if top==True:

            self.labels_top=top_label

        else:

            self.labels_top=None

        if bottom==True:

            self.labels_bottom=[[bottom_label+"{:03d} x {:03d}".format(x,y) \
            for x in range(col_index,col_index+len(self.x_param))] \
            for y in range(row_index,row_index+len(self.y_param))]

        else:

            self.labels_bottom=None

    @property
    def table(self):

        x_param=self.x_param

        y_param=self.y_param

        device=deepcopy(self.device)

        data_tot=DataFrame()

        # import pdb; pdb.set_trace()

        for j in range(len(y_param)):

            device.import_params(DataFrame(y_param(j),index=[0]))

            for i in range(len(x_param)):

                device.import_params(DataFrame(x_param(i),index=[0]))

                df=device.export_params()

                if self.labels_bottom is not None:

                    df.index=[self.labels_bottom[j][i]]

                else:

                    df.index=[i,j]

                data_tot=data_tot.append(df)

        return data_tot
