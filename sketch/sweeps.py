from building_blocks import *

class SweepParam():

    def __init__(self,params):

        if isinstance(params,dict):

            self._dict=params

        else:

            raise ValueError("SweepParam is init by dict of names:values")

    def __call__(self,*args):

        if not args:

            return self._dict

        elif isinstance(args[0],int):

            return {x:y[args[0]] for x,y in zip(self.names,self.values)}

    def __len__(self):
        return len(self._dict[list(self._dict.keys())[0]])

    def __str__(self):

        return str(self._dict)

    __repr__=__str__

    @property
    def labels(self):

        param=self

        l=len(param)

        sweep_label=[]

        # tmp_name=""
        for index,name in enumerate(param.names):

            if index<=1:

                sweep_label.append((\
                ''.join([c for c in name if c.isupper()]))\
                .replace("IDT","")\
                .replace("S","")\
                .replace("M",""))

        stringout=[]

        unique={name:list(dict.fromkeys(values)) for name,values in zip(param.names,param.values)}

        for i in range(l):

            tmp_lab=''

            for lab,name in zip(sweep_label,param.names):

                tmp_lab=tmp_lab+lab+str(unique[name].index(param()[name][i]))

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



        dict_new={x : [] for x in init_names+new_names}



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

                raise ValueError("At least one param key in {} is invalid".format(','.join([*layout_param.names])))

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

class _SweepArrayValidator(_SweepParamValidator):

    def __set__(self,owner,layout_params):

        if not isinstance(layout_params,list):

            if not isinstance(layout_params,SweepParam):

                raise ValueError("a SweepParam instance needs to be passed here")

            else:

                layout_params=[layout_params]

        sweep_row=list()



        for par in layout_params:

            _SweepParamValidator.__set__(self,owner,par)
            sweep_row.append(getattr(owner,self.private_name))

        setattr(owner,self.private_name,sweep_row)

class PArray(LayoutPart):

    x_param=_SweepParamValidator(ld.Arrayx_param)

    def __init__(self,device,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.device=device

        self.x_spacing=ld.Arrayx_spacing

        self.labels_top=ld.Arraylabels_top

        self.labels_bottom=ld.Arraylabels_bottom

        self.text_params=copy(TextParam())

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

        device=self.device

        base_params=device.export_params()

        data_tot=DataFrame()

        for i in range(len(param)):

            for name in param.names:

                device.import_params(param(i))

            df=device.export_params()

            if self.labels_bottom is not None:

                index=self.labels_bottom[i]

            else:

                index=str(i)

            import pdb; pdb.set_trace()

            data_tot=data_tot.append(Series(df,name=index))

            device.import_params(base_params)

        return data_tot

    def import_params(self,df):

        self.device.import_params(df)

    def draw(self):

        device=self.device

        df_original=device.export_params()

        master_cell=Device(self.name)

        cells=list()

        param=self.x_param

        df=copy(df_original)

        for index in range(len(param)):

            for name,value in zip(param.names,param.values):

                df[name]=value[index]

            device.import_params(df)

            print("drawing device {} of {}".format(index+1,len(param)))

            new_cell=device.draw()

            if self.labels_top is not None:

                self.text_params.set('location','top')

                self.text_params.add_text(new_cell,self.labels_top[index])

            if self.labels_bottom is not None:

                self.text_params.set('location','bottom')

                self.text_params.add_text(new_cell,self.labels_bottom[index])

            master_cell<<new_cell

            cells.append(new_cell)

        g=Group(cells)

        g.distribute(spacing=self.x_spacing)

        g.align(alignment='ymin')

        device.import_params(df_original)

        del device, cells ,g

        master_cell=join(master_cell)

        master_cell._internal_name=self.name

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

class PMatrix(PArray):

    y_param=_SweepParamValidator(ld.Matrixy_param)

    def __init__(self,device,*args,**kwargs):

        super().__init__(device,*args,**kwargs)

        self.y_spacing=ld.Matrixy_spacing
        self.labels_top=ld.Matrixlabels_top
        self.labels_bottom=ld.Matrixlabels_bottom

    def draw(self):

        device=self.device

        df_original=device.export_params()

        master_name=self.name

        master_cell=Device(master_name)

        cells=list()

        top_label_matrix=self.labels_top

        bottom_label_matrix=self.labels_bottom

        y_param=self.y_param

        df=copy(df_original)

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

            self.name=master_name+"Arr"+str(index+1)

            new_cell=PArray.draw(self)

            master_cell<<new_cell

            cells.append(new_cell)

        g=Group(cells)

        g.distribute(direction='y',spacing=self.y_spacing)

        g.align(alignment='xmin')

        device.import_params(df_original)

        del device, cells ,g

        self.cell=master_cell

        self.labels_top=top_label_matrix

        self.labels_bottom=bottom_label_matrix

        return master_cell

    def auto_labels(self,top=True,bottom=True,top_label='',bottom_label='',\
        col_index=0,row_index=0):

        y_label=[top_label+x for x  in self.y_param.labels]

        x_label=[top_label+x for x in self.x_param.labels]

        import itertools

        top_label=[[top_label+x+"\n"+y for x in x_label] for y in y_label]

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

        device=self.device

        df_original=device.export_params()

        data_tot=DataFrame()

        for j in range(len(y_param)):

            device.import_params(y_param(j))

            for i in range(len(x_param)):

                device.import_params(x_param(i))

                df=device.export_params()

                if self.labels_bottom is not None:

                    index=self.labels_bottom[j][i]

                else:

                    index=str(i)+str(j)

                data_tot=data_tot.append(Series(df,name=index))

        device.import_params(df_original)

        return data_tot

class PArraySeries(PArray):

    x_param=_SweepArrayValidator(ld.Arrayx_param)

    def __init__(self,device,*a,**k):

        PArray.__init__(self,device,*a,*k)

        self.y_spacing = 100

    def draw(self):

        cellparts=list()

        device=self.device

        df_original=device.export_params()

        df=copy(df_original)

        p=PArray(device)

        for i,par in enumerate(self.x_param):

            p.x_spacing=self.x_spacing

            p.x_param=par

            p.auto_labels(row_index=1,col_index=0)

            cellparts.append(p.draw())

        g=Group(cellparts)

        g.distribute(direction='y',spacing=self.y_spacing)

        g.align(alignment='xmin')

        cell=Device(self.name)

        [cell<<x for x in cellparts]

        self.cell=cell

        device.import_params(df_original)

        return cell

    @property
    def table(self):

        x_param=self.x_param

        data_tot=DataFrame()

        for p in x_param:

            device=deepcopy(self.device)

            parr=PArray(device)

            parr.x_param=p

            data_tot.append(parr.table)

        return data_tot
