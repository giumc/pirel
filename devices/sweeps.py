from building_blocks import *

import matplotlib.pyplot as plt

import matplotlib as mpl

from matplotlib import cm

from matplotlib.ticker import LinearLocator

import numpy as np

plt.style.use(os.path.dirname(__file__)+os.path.sep+'pltstl.mplstyle')

from math import ceil,floor

import sys

class SweepParam():

    """ Class used to generate and combine sweep parameters in PArray/PMatrix.

        More parameters can be swept at the same time by specifying the format
            {name1:values1, name2:values2 } when building SweepParam.

        Parameters
        ----------
            params : dict

                a dict with {name:values} format.

        To call a parameter sweep point, use the following syntax:
            par=SweepParam({"Length":[1,2,3],"Width":[4,5,6]})
            par(0)  ->returns {"Length":1,"Width":4}
            par(1)  ->returns {"Length":2,"Width":5}.
    """

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

        return str({name:[float(f"{x:.2f}") for x in value] for name,value in self._dict.items()})

    __repr__=__str__

    @property
    def labels(self):

        """ parameter sweep names/values  in compact form"""

        param=self

        l=len(param)

        sweep_label=[]

        for index,name in enumerate(param.names):

            sweep_label.append((\
            ''.join([c for c in name if c.isupper()]))\
            .replace("IDT","")\
            .replace("S","")\
            .replace("M",""))

        stringout=[]

        unique={name:list(dict.fromkeys(values)) for name,values in zip(param.names,param.values)}

        for i in range(l):

            tmp_lab=''

            for lab,name in zip(sweep_label,self.names):

                tmp_lab=tmp_lab+lab+str(unique[name].index(param()[name][i]))

            stringout.append(tmp_lab)

        return stringout

    @property
    def names(self):
        """ Iterable of parameter names"""
        return [x for x in self._dict.keys()]

    @property
    def values(self):
        """iterable of parameter values"""
        return [_ for _ in self._dict.values()]

    def combine(self,sweep2):
        """ Combine two SweepParam.

            The parameters are combined with another SweepParam
            instance to generate a new SweepParam.
            If the instance has a length M and the parameter has a length N ,
            resulting SweepParam will have length MxN.

            Parameters
            ----------
                sweep2 : PyResLayout.SweepParam

                    the SweepParam to be combined with the old one.

            Returns
            -------
                sweep : PyResLayout.SweepParam

            Example
            -------
                sw1 = SweepParam({"X":[3,4])
                sw2 = SweepParam({"Y":[5,6])
                sw3 = sw1.combine(sw2)

                # sw3 -> {"X":[3,3,4,4],"Y":[5,6,5,6]}.
        """

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

        return SweepParam(dict_new)

    def populate_plot_axis(self,plot,ax='x'):
        """ Decorate plot axis with SweepParam name/values.

            Parameters
            ----------
                plot : matplotlib.Axes

                ax : str ('x' or 'y').

            The function assumes that the plot ticks have the same length as the
            SweepParam.
        """

        fig=plt.gcf()

        extra_ax=[]

        if ax=='x':

            ticks=plot.get_xticks()

            lim=plot.get_xlim()

            for i in range(len(self.names)):

                if i==0:

                    axn=plot

                    axn.spines['bottom'].set_position(('outward',10))

                    axn.spines['bottom'].set_visible(True)

                else:

                    dy_fig=0.08

                    prev_ax_position=axn.get_position()

                    extra_ax.append(fig.add_axes(\
                        (prev_ax_position.x0,\
                        prev_ax_position.y0-2*dy_fig,\
                        prev_ax_position.width,\
                        0),'autoscalex_on',True))

                    axn=extra_ax[i-1]

                    axn.yaxis.set_visible(False)

                for side in axn.spines.keys():

                    axn.spines[side].set_linewidth(1)

                axn.set_xticks(ticks)

                ticksnames=[float(str(x)) for x in self.values[i]]

                axn.set_xticklabels(\
                    ["{:.2f}".format(x).rstrip('0').rstrip('.') for x in ticksnames],\
                    rotation = 45)

                xlab=axn.set_xlabel(self.names[i])

                xlab.set_fontsize(10)

                axn.tick_params(axis='x',labelsize=10)

                axn.set_xlim(lim)



        elif ax=='y':

            ticks=plot.get_yticks()

            lim=plot.get_ylim()

            for i in range(len(self.names)):

                if i==0:

                    axn=plot

                    axn.spines['left'].set_position(('outward',10))

                    axn.spines['left'].set_visible(True)

                else:

                    dx_fig=0.08

                    plot_position=plot.get_position()

                    prev_ax_position=axn.get_position()

                    extra_ax.append(fig.add_axes(\
                        (prev_ax_position.x0-2*dx_fig,\
                        prev_ax_position.y0,\
                        0,\
                        prev_ax_position.height),'autoscalex_on',True))

                    axn=extra_ax[i-1]

                    axn.xaxis.set_visible(False) # hide the yaxis

                for side in axn.spines.keys():  # 'top', 'bottom', 'left', 'right'

                    axn.spines[side].set_linewidth(1)

                axn.set_yticks(ticks)

                ticksnames=[float(str(x)) for x in self.values[i]]

                axn.set_yticklabels(\
                    ["{:.2f}".format(x).rstrip('0').rstrip('.') for x in ticksnames],\
                    rotation = 45)

                ylab=axn.set_ylabel(self.names[i])

                ylab.set_fontsize(10)

                axn.tick_params(axis='y',labelsize=10)

                axn.set_ylim(lim)

        else:

            raise ValueError("Axis can be 'x' or 'y'")

    def subset(self,n):
        """ Downsample sweep parameters.

            Parameter
            ---------
                n : int

                    new length of the SweepParam (needs to be smaller than original length).

            Returns
            -------
                sweep : PyResLayout.SweepParam

                    a new SweepParam with "downsampled" values.
        """

        if n>=len(self):

            warning.warn(f""" SweepParam.subset : {n} larger than SweepParam length ({len(self)})""")

            return self

        from numpy import ceil

        if len(self)%2==1:

            spacing=int(floor((len(self)+1)/n))

        else:

            spacing=int(floor(len(self)/n))

        new_dict={}

        for name in self.names:

            old_values=self._dict[name]

            new_values=[old_values[x] for x in range(0,len(self)-1,spacing)]

            if not len(new_values)==n:

                import pdb; pdb.set_trace()
                raise ValueError("bug in subset creation, wrong length")

            else:

                new_dict[name]=new_values

        return SweepParam(new_dict)

class _SweepParamValidator():

    def __init__(self,def_param=LayoutDefault.Arrayx_param):

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

            self._set_valid_names([*obj.export_params().keys()])

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

class PArray(LayoutPart):

    """ Class used to create a parametric array of cells.

        Parameters
        ----------

            device : PyResLayout.LayoutPart

            x_param : PyResLayout.SweepParam

                every of the x_param.names has to be a parameter of device.
    """

    x_param=_SweepParamValidator(LayoutDefault.Arrayx_param)

    def __init__(self,device,x_param,*args,**kwargs):

        if 'name' in kwargs.keys():

            self.name=kwargs['name']

        else:

            self.name='Default'

        self.device=device

        self.x_param=x_param

        self.x_spacing=LayoutDefault.Arrayx_spacing

        self.labels_top=LayoutDefault.Arraylabels_top

        self.labels_bottom=LayoutDefault.Arraylabels_bottom

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

            self.device.name=self.name

    def export_params(self):

        return self.device.export_params()

    def export_all(self):

        return self.device.export_all()

    @property
    def table(self):

        """ A pandas.DataFrame that represent all the parameters in PArray.device """

        param=self.x_param

        device=self.device

        base_params=device.export_params()

        data_tot=DataFrame()

        for i in range(len(param)):

            print_index=1

            for name in param.names:

                device.import_params(param(i))

            df=device.export_all()

            if self.labels_bottom is not None:

                index=self.labels_bottom[i]

            else:

                index=str(i)

            print("Generating table, item {} of {}\r".format(print_index,len(param)),end="")

            data_tot=data_tot.append(Series(df,name=index))

            device.import_params(base_params)

        return data_tot

    def import_params(self,df):

        self.device.import_params(df)

    def draw(self):

        device=self.device

        df_original=device.export_params()

        master_cell=Device(name=self.name)

        cells=list()

        param=self.x_param

        df={}

        for key,val in df_original.items():

            if callable(val):

                df[key]=val

        for index in range(len(param)):

            for name,value in zip(param.names,param.values):

                df[name]=value[index]

            device.import_params(df)

            # print("drawing device {} of {}".format(index+1,len(param)),end="\r")

            new_cell=Device()
            new_cell.absorb(new_cell<<device.draw())
            new_cell=join(new_cell)

            master_cell<<new_cell

            new_cell.name=self.name+"_"+str(index+1)

            if self.labels_top is not None:

                self.text_params.set('location','top')

                self.text_params.add_text(new_cell,self.labels_top[index])

            if self.labels_bottom is not None:

                self.text_params.set('location','bottom')

                self.text_params.add_text(new_cell,self.labels_bottom[index])

            cells.append(new_cell)

        g=Group(cells)

        g.distribute(spacing=self.x_spacing)

        g.align(alignment='ymin')

        device.import_params(df_original)

        del device, cells ,g

        return master_cell

    def auto_labels(self,top=True,bottom=True,top_label='',bottom_label='',\
        col_index=0,row_index=0):

        """Generate automatically labels to attach to array cells.

            resulting labels are stored in "labels_top" and "labels_bottom"
            attributes.

            Parameters
            ----------
                top : Boolean

                    True/False controls creation of top labels

                bottom : Boolean

                    same as top

                top_label : str

                    common optional prefix to attach to top label

                bottom_label : str

                    common optional prefix to attach to bottom label

                col_index : int

                    offset for column indexing (used in bottom label)

                row_index : int

                    offset for row indexing (used in bottom label).
        """
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

    def plot_param(self,param,blocking=True):

        """Plots a parameter taken from export_all() across all swept cells.

            Parameter
            ---------
                param : str

                    has to be a key in the dict returned by export_all()

                blocking : Boolean

                    if True, blocks script when method is called

            Returns
            -------
                fig : matplotlib.Figure.
        """
        import matplotlib.pyplot as plt
        from matplotlib import cm
        from matplotlib.ticker import LinearLocator
        import numpy as np

        fig, ax = plt.subplots()

        sweep_param=self.x_param

        df_original=self.export_params()

        if isinstance(param,str):

            param=[param]

        if len(param)==1:

            y = []

            for i in range(len(sweep_param)):

                self.import_params(sweep_param(i))

                df=self.export_all()

                y.append(df[param[0]])

            p=ax.scatter([_+1 for _ in range(len(y))],y)

            p.set_clip_on(False)

            ax.set_ylabel(param[0])

        elif len(param)>1:

            y=[]
            p=[]

            for j in range(len(param)):

                y.append([])

                for i in range(len(sweep_param)):

                    self.import_params(sweep_param(i))

                    df=self.export_all()

                    y[j].append(df[param[j]])

                p.append(ax.scatter([_+1 for _ in range(len(y[j]))],y[j],label=param[j]))

                p[j].set_clip_on(False)

            ax.set_ylabel(", ".join(param))

            ax.legend()

        ax.grid(linestyle='--',linewidth=0.5, color='grey')

        ax.autoscale(enable=True, tight=True)

        self.x_param.populate_plot_axis(ax)

        self.import_params(df_original)

        plt.show()

        return fig

class PMatrix(PArray):

    y_param=_SweepParamValidator(LayoutDefault.Matrixy_param)

    def __init__(self,device,x_param,y_param,*a,**k):

        super().__init__(device,x_param,*a,*k)
        self.y_spacing=LayoutDefault.Matrixy_spacing
        self.y_param=y_param
        self.labels_top=LayoutDefault.Matrixlabels_top
        self.labels_bottom=LayoutDefault.Matrixlabels_bottom

    def draw(self):

        device=self.device

        df_original=device.export_params()

        master_name=self.name

        master_cell=Device(master_name)

        cells=list()

        top_label_matrix=self.labels_top

        bottom_label_matrix=self.labels_bottom

        y_param=self.y_param

        x_param=self.x_param

        df={}

        for key in df_original.keys():

            if callable(df_original[key]):

                df.update({key:df_original[key]})

        for index in range(len(y_param)):

            for name,value in zip(y_param.names,y_param.values):

                df[name]=value[index]

            device.import_params(df)

            print("drawing array {} of {}".format(index+1,len(y_param)),end='\r')

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

            print("\033[K",end='')

            master_cell<<new_cell

            cells.append(new_cell)

        g=Group(cells)

        g.distribute(direction='y',spacing=self.y_spacing)

        g.align(alignment='x')

        device.import_params(df_original)

        del device, cells ,g

        self.labels_top=top_label_matrix

        self.labels_bottom=bottom_label_matrix

        self.name=master_name

        return master_cell

    def auto_labels(self,top=True,bottom=True,top_label='',bottom_label='',\
        col_index=0,row_index=0):

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

        device=self.device

        df_original=device.export_params()

        data_tot=DataFrame()

        print_index=1

        for j in range(len(y_param)):

            device.import_params(y_param(j))

            for i in range(len(x_param)):

                device.import_params(x_param(i))

                df=device.export_all()

                if self.labels_bottom is not None:

                    index=self.labels_bottom[j][i]

                else:

                    index=str(i)+str(j)

                print("Generating table, item {0} of {1}".format(print_index,str(len(x_param)*len(y_param))),end="\r")
                print("\033[K",end='')
                # sys.stdout.flush()

                print_index+=1

                data_tot=data_tot.append(Series(df,name=index))

        device.import_params(df_original)

        return data_tot

    def plot_param(self,param):

        fig, ax = plt.subplots()

        sweep_param_x=self.x_param

        sweep_param_y=self.y_param

        df_original=self.export_params()

        x=[*range(len(sweep_param_x))]

        y=[*range(len(sweep_param_y))]

        z=[]

        print_index=1

        for j in y:

            z.append([])

            for i in x:

                self.import_params(sweep_param_x(i))
                self.import_params(sweep_param_y(j))

                df=self.export_all()

                print("Getting {} value , item {} of {} ".format(param,print_index,len(x)*len(y)),end="\r")
                # sys.stdout.flush()
                print("\033[K",end='')
                z[j].append(df[param])
                print_index+=1

        x=np.array(x)
        y=np.array(y)
        z=np.array(z)
        x,y=np.meshgrid(x,y)

        cmap=plt.cm.viridis

        import seaborn as sns

        surf=sns.heatmap(z,cmap='viridis',linewidth=0.5)

        plt.gcf().suptitle(param, fontsize=12)

        ax.set_xticks([_+0.5 for _ in range(len(sweep_param_x))])
        ax.set_yticks([_-0.5 for _ in range(len(sweep_param_y),0,-1)])

        self.x_param.populate_plot_axis(ax,'x')
        self.y_param.populate_plot_axis(ax,'y')

        self.import_params(df_original)

        return fig
