import ROOT as r
import numpy as np
from prettytable import PrettyTable
import tabulate as tabulate
import matplotlib.pyplot as plt
import mplhep as hep
plt.style.use(hep.style.ROOT)
import tdrstyle
from scipy.interpolate import interp1d
tdrstyle.setTDRStyle()
r.gStyle.SetPadTopMargin(0.10)
r.gStyle.SetPadLeftMargin(0.2)
r.gStyle.SetPadRightMargin(0.2)
r.gStyle.SetPadBottomMargin(0.15)
r.gStyle.SetPaintTextFormat("1.1f")
r.gStyle.SetOptFit(0000)
r.gROOT.SetBatch()

def printGenYield(f,mdfs,year,binnings):
    tf = r.TFile(f)
    yields = []
    for s in ['h_ggHbb_fBosonPt_weight','h_ggHbb_NNLOPS_fBosonPt_weight']:
        if 'NNLOPS' in s: sample = 'MiNLO'
        else:             sample = 'POWHEG'
        #print sample
        h_gen_norm = tf.Get(s)
        data = {'sample':sample,'year':year,'binnings':binnings}
        norms =[]
        bins =[]
        for ibin,genpt in enumerate(binnings):
            if ibin < len(binnings)-1:
                bin_lo = genpt
                bin_up = binnings[ibin+1]
                norm_bin_lo = h_gen_norm.FindBin(bin_lo)
                norm_bin_up = h_gen_norm.FindBin(bin_up)
                norm   = h_gen_norm.Integral(norm_bin_lo,norm_bin_up)
                norms.append(norm)
                #print year,'  sample = %s [bin_low,bin_up]=[%1.f,%.1f]  yield = %.3f'%(sample,bin_lo,bin_up,norm)
        data['norms']=norms
        for mdf in mdfs:
            pamVal,pamValHi,pamValLo = getMus(mdf)
            #print mdf,  pamVal,pamValHi,pamValLo
            if (sample=="MiNLO" and 'minlo' in mdf) or (sample=="POWHEG" and not 'minlo' in mdf):
                data['r']   = [float('%.5f'%p) for p in pamVal]
                data['rHi'] = [float('%.5f'%p) for p in pamValHi]
                data['rLo'] = [float('%.5f'%p) for p in pamValLo]
        yields.append(data)
    #for y in yields:        print y
    return yields

def getCombdata(mdfs,binnings):
    yields=[]
    for sample in ['MiNLO','POWHEG']:
        data= {'year':'comb','sample':sample,'binnings':binnings}
        for mdf in mdfs:
            pamVal,pamValHi,pamValLo = getMus(mdf)
            #print mdf,  pamVal,pamValHi,pamValLo
            if (sample=="MiNLO" and 'minlo' in mdf) or (sample=="POWHEG" and not 'minlo' in mdf):
                data['r']   = [float('%.5f'%p) for p in pamVal]
                data['rHi'] = [float('%.5f'%p) for p in pamValHi]
                data['rLo'] = [float('%.5f'%p) for p in pamValLo]
        yields.append(data)
    return yields

def getrs(allyields,year,sample):
    data={}
    (data['r'],data['rHi'],data['rLo']) = ([],[],[])
    for data in allyields:
        if data['sample']==sample and data['year'] == year:
            return data['r'],data['rHi'],data['rLo']
    return data['r'],data['rHi'],data['rLo']

def getXS(allyields,year,sample):
    data={}
    (data['xs'],data['xsHi'],data['xsLo']) = ([],[],[])
    for data in allyields:
        if data['sample']==sample and data['year'] == year:
            return data['xs'],data['xsHi'],data['xsLo']
    return data['xs'],data['xsHi'],data['xsLo']
def getYield(allyields,year,sample):
    data={}
    (data['norms']) = ([])
    for data in allyields:
        if data['sample']==sample and data['year'] == year:
            return data['norms']
    return data['norms']


def calXS(allyields,year,sample): 
    Minlo_perBinYield  = np.array([0 for i in range(1,len(allyields[0]['binnings']))])
    Minlo_perBinXS  = np.array([0 for i in range(1,len(allyields[0]['binnings']))])
    if year is not 'comb':
        for data in allyields:
            lumi = 0.0
            if data['year']=='2016': lumi = 35.9
            elif data['year']=='2017': lumi = 41.4
            elif data['year']=='2018': lumi = 59.2
        
            if data['sample']==sample and data['year'] == year:
                Minlo_perBinYield  = np.add(  Minlo_perBinYield, np.array(data['norms']))
                Minlo_perBinXS     = np.multiply( np.array(data['norms'])/(lumi*0.58), np.array(data['r']))
                Minlo_perBinXShi   = np.multiply( np.array(data['norms'])/(lumi*0.58), np.array(data['rHi']))
                Minlo_perBinXSlo   = np.multiply( np.array(data['norms'])/(lumi*0.58), np.array(data['rLo']))
                #Minlo_perBinXS     =  np.array(data['norms'])/(lumi*0.58)
                #Minlo_perBinXShi   =  np.array(data['norms'])/(lumi*0.58)
                #Minlo_perBinXSlo   =  np.array(data['norms'])/(lumi*0.58)
                data['xs']  =Minlo_perBinXS.tolist()
                data['xsHi']=Minlo_perBinXShi.tolist()
                data['xsLo']=Minlo_perBinXSlo.tolist()
                
    else:
        comb_r = {}
        for yr in ['2016','2017','2018']:
            for data in allyields:
                if data['sample']==sample and data['year'] == yr:
                    Minlo_perBinYield  = np.add(  Minlo_perBinYield, np.array(data['norms']))                    ## Sum the norms
                elif data['sample']==sample and data['year'] == 'comb':
                    comb_r = data                                                       # find the comb data 
        lumi = 136.2
        Minlo_perBinXS     = np.multiply( Minlo_perBinYield/(lumi*0.58), np.array(comb_r['r']))
        Minlo_perBinXShi   = np.multiply( Minlo_perBinYield/(lumi*0.58), np.array(comb_r['rHi']))
        Minlo_perBinXSlo   = np.multiply( Minlo_perBinYield/(lumi*0.58), np.array(comb_r['rLo']))
        comb_r['xs']   = Minlo_perBinXS.tolist()
        comb_r['xsHi'] = Minlo_perBinXShi.tolist()
        comb_r['xsLo'] = Minlo_perBinXSlo.tolist()
        comb_r['norms'] = Minlo_perBinYield.tolist()

    #print year
    #print '%s gen yields = '%sample, ['%.3f'%i for i in Minlo_perBinYield ]
    #print '%s XS         = '%sample, ['%.3f'%i for i in Minlo_perBinXS ]
    #print '%s XS_lo      = '%sample, ['%.3f'%i for i in Minlo_perBinXShi ]
    #print '%s XS_hi      = '%sample, ['%.3f'%i for i in Minlo_perBinXSlo ]
    #return Minlo_perBinYield,Minlo_perBinXS,Minlo_perBinXShi,Minlo_perBinXSlo
    return allyields 


def getMus(multidimfit):
    f     = r.TFile(multidimfit)
    rfr   = f.Get("fit_mdf")
    fitpams = rfr.floatParsFinal().selectByName("r_*")
    fitpamNames = sorted([ fitpams[i].GetName() for i in range(0,len(fitpams))])
    pamVal = []
    pamValHi = []
    pamValLo = []
    if len(fitpamNames)==0: print "Cannot find any fit pams with r_*"
    for p in fitpamNames:
        #print p, "= %.3f"%rfr.floatParsFinal().find(p).getVal(), "+%.3f/%.3f"%( rfr.floatParsFinal().find(p).getErrorHi(),rfr.floatParsFinal().find(p).getErrorLo())
        pamVal.append(  float(rfr.floatParsFinal().find(p).getVal()))
        pamValHi.append(float(rfr.floatParsFinal().find(p).getErrorHi()))
        pamValLo.append(float(rfr.floatParsFinal().find(p).getErrorLo()))
    return pamVal,pamValHi,pamValLo
 
def addRows(table,Fits,allyields,sample):
    binnings = Fits['binnings']
    rows = []
    rows.append(['-' for i in table.field_names])
    for ibin,genpt in enumerate(binnings):
        if ibin < len(binnings)-1:
            bin_lo = genpt
            bin_up = binnings[ibin+1]
            tablerow=['[%s,%s] mu'%(bin_lo,bin_up)]
    
            for year in ['2016','2017','2018','comb']:
                rS,rhi,rlo            = getrs(allyields,year,sample)
                #tablerow.append( "%.2f +%.2f/%.2f"% (rS[ibin],rhi[ibin],rlo[ibin]))
                tablerow.append( "$%.2g^{+%.2g}_{%.2g}$"% (rS[ibin],rhi[ibin],rlo[ibin]))
            rows.append(tablerow)
    rows.append(['-' for i in table.field_names])
    for ibin,genpt in enumerate(binnings):
        if ibin < len(binnings)-1:
            bin_lo = genpt
            bin_up = binnings[ibin+1]
            tablerow=['[%s,%s] $\sigma$(fb)'%(bin_lo,bin_up)]
            for year in ['2016','2017','2018','comb']:
                XS,XShi,XSlo    = getXS(allyields,year,sample)
                #tablerow.append( "%.2f +%.2f/%.2f"% (XS[ibin],XShi[ibin],XSlo[ibin]))
                tablerow.append( "$%.2g^{+%.2g}_{%.2g}$"% (XS[ibin],XShi[ibin],XSlo[ibin]))
            rows.append(tablerow)
    rows.append(['-' for i in table.field_names])
    for ibin,genpt in enumerate(binnings):
        if ibin < len(binnings)-1:
            bin_lo = genpt
            bin_up = binnings[ibin+1]
            tablerow=['[%s,%s] Yield'%(bin_lo,bin_up)]
            for year in ['2016','2017','2018','comb']:
                norms    = getYield(allyields,year,sample)
                tablerow.append( "%.2f "% (norms[ibin]))
            rows.append(tablerow)
    return rows
   

def printTable():
    for s in ['MiNLO','POWHEG']:
        table = PrettyTable()
        allrows =[]
        colnames = ['bin','2016','2017','2018','comb']
        allrows.append(colnames)
        table.field_names = colnames
        table.add_row([s,'-','-','-','-'])
        allrows.append([s,'-','-','-','-'])
    
        for Fits in [Fits_stxs,Fits_450,Fits_fine]:
            allyields =  printGenYield(gen2016,Fits['mdf2016s'],'2016',Fits['binnings'])
            allyields += printGenYield(gen2017,Fits['mdf2017s'],'2017',Fits['binnings'])
            allyields += printGenYield(gen2018,Fits['mdf2018s'],'2018',Fits['binnings'])
            allyields += getCombdata(Fits['mdfcomb'],Fits['binnings'])
            for year in ['2016','2017','2018','comb']:
                allyields = calXS(allyields,year,s)
    
            print Fits['binnings']
            print "Printing raw yields..."
            #for y in allyields: print y
            print "Formatting into tables..."
            rows = addRows(table,Fits,allyields,s)
            for row in rows:
                table.add_row(row)
                allrows.append(row)
        table.align['bin']='l'
        
        #print table
        print tabulate.tabulate(allrows,headers="firstrow",tablefmt="latex_raw")


def getData(t, sample,year,rOrXs,selectedBin =[]):
    # y == int, string of binnings
    # x == r or XS
    y,ylabels,yerr = [],[],[[],[]]
    x,xHi,xLo = [],[],[]
    bins =[
        {'b':[350, 600, 12000]     ,'ylabels':['350-600 GeV','>600GeV']},
        {'b':[450,  12000]         ,'ylabels':['> 450 GeV']},
        {'b':[450, 550, 675, 12000],'ylabels':['450-550 GeV','550-675 GeV','>675 GeV']},
        {'b':[300, 450, 650, 12000],'ylabels':['300-450 GeV','450-650 GeV','>650 GeV']},
        {'b':[450, 650, 12000],'ylabels':['450-650 GeV','>650 GeV']},
    ]
    for b in bins:
        if len(selectedBin)>0 and not b['b'] in selectedBin: continue
        ylabels += b['ylabels']
        for row in t:
            if row['sample']==sample and row['binnings']==b['b'] and row['year']==year:
                if rOrXs=='r':
                    x+= row['r']
                    xHi+=row['rHi']
                    xLo+=row['rLo']
                else:
                    x  +=row['xs']
                    xHi+=row['xsHi']
                    xLo+=row['xsLo']
    if len(selectedBin)>0:
        for sb in selectedBin:         
           y += [ (sb[i]+min([sb[i+1],1200]))/2 for i,b in enumerate(sb) if i <len(sb)-1]
           yerr_low = [(min([sb[i+1],1200])-sb[i])/2 for i,b in enumerate(sb) if i <len(sb)-1]
           yerr_up  = [(min([sb[i+1],1200])-sb[i])/2 for i,b in enumerate(sb) if i <len(sb)-1]
           yerr =[ yerr_low, yerr_up]
           binWidths = np.diff(np.minimum([1200]*len(sb),np.array(sb)))
        print y 
    else:
        y = [ i*6 for i in  range(0,len(ylabels))]
    xs =np.array(x)/binWidths
    xs_err = [abs(np.array(xLo))/binWidths,np.array(xHi)/binWidths]
    print 'xs          =',np.array(x)
    print 'xs/binWidths=',np.array(x)/binWidths

    return np.array(y),xs,xs_err,yerr,ylabels

def getLHCXS(diff):
    # from https://indico.cern.ch/event/810995/contributions/3379473/attachments/1829211/2995039/theory_talk_ggF.pdf
    ## use ptcuts straight from theory
    if diff==False: 
        ptcuts   = np.array([400.0,450.0,500,550,600,650,700,750,800])
        pt_err   = ptcuts* 0.0 
        xs       = np.array([32.03,17.37,9.66,5.54,3.24,1.94,1.15,0.69,0.41])
        ## in percentage
        xs_up_percent    = np.array([9.09,8.9,8.86,8.76,8.73,8.66,8.56,8.53,8.47])
        xs_down_percent  = np.array([-11.55,-11.50,-11.49,-11.45,-11.28,-11.28,-11.24,-11.27,-11.18])
        xs_up            =  xs   * xs_up_percent/100.
        xs_down          =  xs   * xs_down_percent/100.
        
        return pt,pt_err,xs,[xs_up,xs_down]
    else:
        ptcuts   = np.array([400.0,450.0,500,550,600,650,700,750,800])
        pt       = (ptcuts[:-1] + ptcuts[1:])/2.
        pt_up    = (ptcuts[1:] - ptcuts[:-1])/2.
        pt_low   = (ptcuts[1:] - ptcuts[:-1])/2.
        pt_err   = [pt_up,pt_low]

        xs           = np.array([32.03,17.37,9.66,5.54,3.24,1.94,1.15,0.69,0.41])
        diffxs       = np.diff(xs)*(-1)/ np.diff(ptcuts)
        xs_up_percent    = np.array([9.09,8.9,8.86,8.76,8.73,8.66,8.56,8.53,8.47])
        xs_down_percent  = np.array([-11.55,-11.50,-11.49,-11.45,-11.28,-11.28,-11.24,-11.27,-11.18])
        xs_up            =  (xs   * xs_up_percent/100.)
        xs_down          =  abs(xs   * xs_down_percent/100.)
        diffxs_up        =  ((xs_up[1:]+xs_up[:-1])/2) /np.diff(ptcuts)        ## assume average unc.
        diffxs_down      =  ((xs_down[1:]+xs_down[:-1])/2 )/np.diff(ptcuts)
        diffxs_err       = [diffxs_up,diffxs_down]
        #print 'diffxs=',diffxs
        #print 'diffxs_up=',diffxs_up
        #print 'diffxs_down=',diffxs_down
        return pt,pt_err,diffxs,diffxs_err

def getintPrediction4ratio(data_pt,data_xs,data_xs_err,thy_pt,thy_xs,thy_xs_err,edges):
    print edges
    print data_pt
    ptcuts   = np.array([400.0,450.0,500,550,600,650,700,750,800])
    xs       = np.array([32.03,17.37,9.66,5.54,3.24,1.94,1.15,0.69,0.41])
    xs_up_percent    = np.array([9.09,8.9,8.86,8.76,8.73,8.66,8.56,8.53,8.47])
    xs_down_percent  = np.array([-11.55,-11.50,-11.49,-11.45,-11.28,-11.28,-11.24,-11.27,-11.18])
    xs_up            =  (xs   * xs_up_percent/100.)
    xs_down          =  abs(xs   * xs_down_percent/100.)

    interp_xswg      = interp1d(ptcuts, xs, kind='cubic',fill_value='extrapolate') 
    interp_xswg_up   = interp1d(ptcuts, xs_up, kind='cubic',fill_value='extrapolate') 
    interp_xswg_down = interp1d(ptcuts, xs_down, kind='cubic',fill_value='extrapolate') 
    ## don't do extrapolate


    if edges==[450,650]:
        pred_xs    = np.array( [(xs[1]-xs[5])/(ptcuts[5]-ptcuts[1]),xs[5]/550.])
        pred_xs_err = [ np.array([(xs_up[1]-xs_up[5])/(ptcuts[5]-ptcuts[1]),xs_up[5]/550]),np.array([(xs_down[1]-xs_down[5])/(ptcuts[5]-ptcuts[1]),xs_down[5]/550])]
    elif edges==[450]:
        pred_xs    = np.array( [xs[1]/750.])
        pred_xs_err = [ np.array([xs_up[1]/750]),np.array([xs_down[1]/750])]
    elif edges==[450,550,675]:
        pred_xs    = np.array( [(xs[1]-xs[3])/(ptcuts[3]-ptcuts[1]),
                                (xs[3]-interp_xswg(675))/(675-ptcuts[3]),
                                (interp_xswg(675))/(1200-675)])
        pred_xs_err = [
                        np.array( [(xs_up[1]-xs_up[3])/(ptcuts[3]-ptcuts[1]),
                                   (xs_up[3]-interp_xswg_up(675))/(675-ptcuts[3]),
                                   (interp_xswg_up(675))/(1200-675)]),
                        np.array( [(xs_down[1]-xs_down[3])/(ptcuts[3]-ptcuts[1]),
                                   (xs_down[3]-interp_xswg_down(675))/(675-ptcuts[3]),
                                   (interp_xswg_down(675))/(1200-675)])
                        ]
    ratio        = data_xs/pred_xs 
    ratio_err    = data_xs/pred_xs 
    ratio_err      = [data_xs_err[0]/pred_xs, data_xs_err[1]/pred_xs]
    ratio_thy      = pred_xs/pred_xs
    ratio_thy_err  = [pred_xs_err[0]/pred_xs, pred_xs_err[1]/pred_xs]
    print 'prediction    = ',pred_xs,' at these pts ',data_pt
    print 'prediction unc= ',pred_xs_err,' at these pts ',data_pt
    return (ratio,ratio_err,ratio_thy,ratio_thy_err)

def getPrediction4ratio(data_pt,data_xs,data_xs_err,thy_pt,thy_xs,thy_xs_err):
    interp_xswg      = interp1d(thy_pt, thy_xs, kind='cubic',fill_value='extrapolate') 
    interp_xswg_up   = interp1d(thy_pt, thy_xs_err[0], kind='cubic',fill_value='extrapolate') 
    interp_xswg_down = interp1d(thy_pt, thy_xs_err[1], kind='cubic',fill_value='extrapolate') 
    ## don't do extrapolate
    pred_xs        =  interp_xswg(data_pt)
    pred_xs_err    = [interp_xswg_up(data_pt),interp_xswg_down(data_pt)]
    ratio          = data_xs/pred_xs
    ratio_err      = [data_xs_err[0]/pred_xs, data_xs_err[1]/pred_xs]
    ratio_thy      = pred_xs/pred_xs
    ratio_thy_err  = [pred_xs_err[0]/pred_xs, pred_xs_err[1]/pred_xs]
    print 'prediction = ',pred_xs,' at these pts ',data_pt
    return (ratio,ratio_err,ratio_thy,ratio_thy_err)

# binning comparision xS/r v.s. pT
def binningPlot():
    for sample in ['MiNLO','POWHEG']:
        for poi in ['r','xs']:
            fig, ax = plt.subplots()
            y,x,xerr,ylabels  = getData(finalformated_table,sample,'2016',poi)
            ax.errorbar(x, y, xerr=xerr, linestyle='none', marker='.', markersize=10, capsize=10, label ='2016')
            y,x,xerr,ylabels  = getData(finalformated_table,sample,'2017',poi)
            ax.errorbar(x, y+1, xerr=xerr, linestyle='none', marker='.', markersize=10, capsize=10,label='2017')
            y,x,xerr,ylabels  = getData(finalformated_table,sample,'2018',poi)
            ax.errorbar(x, y+2, xerr=xerr, linestyle='none', marker='.', markersize=10, capsize=10,label='2018')
            y,x,xerr,ylabels  = getData(finalformated_table,sample,'comb',poi)
            ax.errorbar(x, y+3, xerr=xerr, linestyle='none', marker='.', markersize=10, capsize=10,label='comb')
            
            print y+3
            ax.axhline(10.5, color='black', lw=1)
            ax.axhline(16.5, color='black', lw=1)
            ax.legend(title=sample)
            if poi =='r':
                xTitle =  'Mu'
            else:
                xTitle =  'Fiducial cross section (fb)'
            plt.xlabel(xTitle)
            plt.yticks(y,ylabels)
            fig.savefig('%s_%s.pdf'%(sample,poi),bbox_inches='tight')


# xS/r v.s. pT
def moneyplot():
    #### format the data for making plots:
    finalformated_table = []
    for Fits in [Fits_stxs,Fits_450,Fits_fine]:
        formated_table = printGenYield(gen2016,Fits['mdf2016s'],'2016',Fits['binnings'])
        formated_table += printGenYield(gen2017,Fits['mdf2017s'],'2017',Fits['binnings'])
        formated_table += printGenYield(gen2018,Fits['mdf2018s'],'2018',Fits['binnings'])
        formated_table += getCombdata(Fits['mdfcomb'],Fits['binnings'])
        #for s in ['MiNLO','POWHEG']:
        for s in ['MiNLO']:
            for year in ['2016','2017','2018','comb']:
                formated_table = calXS(formated_table,year,s)
        finalformated_table+=formated_table

    for sample in ['MiNLO']:
        for poi in ['xs']:
            for year in ['comb']:
                fig, (ax,ax2) = plt.subplots(2,sharex=True,gridspec_kw={'hspace': 0,"height_ratios": (3, 1)})
                if year=='comb':
                    text = 'Observed'
                else:
                    text = year
                data_pt,data_xs,data_xs_err,data_pt_err,ylabels  = getData(finalformated_table,sample,year,poi,[[300, 450, 650, 12000]])   ## new stxs
                ## not show underflow bin
                data_pt,data_xs = data_pt[1:],data_xs[1:]
                data_xs_err = np.array([ data_xs_err[0][1:],data_xs_err[1][1:]])
                data_pt_err = np.array([ data_pt_err[0][1:],data_pt_err[1][1:]])
                print 'data_pt',data_pt
                print 'data_xs',data_xs
                obs = ax.errorbar(data_pt, data_xs, xerr=data_pt_err,yerr=data_xs_err, linestyle='none', marker='.', markersize=10, capsize=0,label='%s'%text)

                thy_pt,thy_pt_err,thy_xs,thy_xs_err  = getLHCXS(diff=True)
                theory = ax.errorbar(thy_pt, thy_xs, xerr=thy_pt_err, linestyle='none' ,label='LHCHXSWG approx. NNLO',color='gray',lw=2)
                print 'thy_pt',thy_pt
                print 'thy_xs',thy_xs
                edges = [400.0,450.0,500,550,600,650,700,750,800]
                y_down_shade = thy_xs-thy_xs_err[1]
                y_up_shade   = thy_xs+thy_xs_err[0]
                y_up_shade   = np.r_[y_up_shade,y_up_shade[-1]]
                y_down_shade   = np.r_[y_down_shade,y_down_shade[-1]]
                shade = ax.fill_between(edges,y_down_shade, y_up_shade,step="post",hatch='///', linewidth= 0,facecolor='none')

                ## numbers for ratio plots, integraed
                (ratio,ratio_err,ratio_thy,ratio_thy_err) = getintPrediction4ratio(data_pt,data_xs,data_xs_err,thy_pt,thy_xs,thy_xs_err,[450,650])

                #print (ratio,ratio_thy)
                ax2.errorbar(data_pt, ratio    , xerr=data_pt_err,yerr=ratio_err  , linestyle='none', marker='.', markersize=10, capsize=0)
                ax2.errorbar(data_pt, ratio_thy, xerr=data_pt_err,yerr=ratio_thy_err, linestyle='none',color='gray',lw=2 )

                ratio_y_down_shade = ratio_thy-ratio_thy_err[1]
                ratio_y_up_shade   = ratio_thy+ratio_thy_err[0]
                ratio_y_up_shade   = np.r_[ratio_y_up_shade,ratio_y_up_shade[-1]]
                ratio_y_down_shade   = np.r_[ratio_y_down_shade,ratio_y_down_shade[-1]]

                data_pt_up = data_pt + data_pt_err[0]
                data_pt_down = data_pt - data_pt_err[0]
                data_pt = np.minimum(1200,np.r_[data_pt_down, data_pt_up[-1]])
                ax2.fill_between(data_pt, ratio_y_down_shade, ratio_y_up_shade ,step='post',hatch='///',lw=0,facecolor='none')
                
                ax.axhline(0, color='black', lw=1)
                ax.legend(title=" ")
                ax.legend([obs,(theory,shade)], ['Observed','LHCHXSWG approx. NNLO'],loc=1)
                if poi =='r':
                    yTitle =  'Mu'
                else:
                    yTitle =  '$\mathrm{\Delta \sigma/\Delta p_T^H}$ (fb/GeV) '
                ax = hep.cms.cmslabel(ax, data=True, paper=False, year='136.2 $\mathrm{fb^{-1}}$')
                ax2.set_xlabel(r"$\mathrm{p_T^H}$ (GeV)", x=1, ha='right')
                ax2.set_ylabel(r"Data/prediction")
                ax.set_ylabel(r'%s'%yTitle, y=1, ha='right')
                ax.set_yscale('log')
                fig.savefig('./genpt/%s_%s_%s.pdf'%(sample,poi,year),bbox_inches='tight')
                fig.savefig('./genpt/%s_%s_%s.png'%(sample,poi,year),bbox_inches='tight')

def binningComp():
    #### format the data for making plots:
    finalformated_table = []
    for Fits in [Fits_stxs,Fits_450,Fits_fine]:
        formated_table = printGenYield(gen2016,Fits['mdf2016s'],'2016',Fits['binnings'])
        formated_table += printGenYield(gen2017,Fits['mdf2017s'],'2017',Fits['binnings'])
        formated_table += printGenYield(gen2018,Fits['mdf2018s'],'2018',Fits['binnings'])
        formated_table += getCombdata(Fits['mdfcomb'],Fits['binnings'])
        for s in ['MiNLO','POWHEG']:
        #for s in ['MiNLO']:
            for year in ['2016','2017','2018','comb']:
                formated_table = calXS(formated_table,year,s)
        finalformated_table+=formated_table

    for sample in ['MiNLO','POWHEG']:
        for poi in ['xs']:
            for year in ['comb']:
                fig, (ax,ax2) = plt.subplots(2,sharex=True,gridspec_kw={'hspace': 0,"height_ratios": (3, 1)})
                #x,y,yerr,xerr,ylabels  = getData(finalformated_table,sample,year,poi,[[450,12000]])
                #ax.errorbar(x, y, xerr=xerr,yerr=yerr, linestyle='none', marker='.', markersize=10, capsize=5,label='%s,pT>450GeV'%year)
                #x,y,yerr,xerr,ylabels  = getData(finalformated_table,sample,year,poi,[[350,600,12000]])
                #ax.errorbar(x, y, xerr=xerr,yerr=yerr, linestyle='none', marker='.', markersize=10, capsize=5,label='%s,STXS'%year)
                if year=='comb':
                    text = 'Observed'
                else:
                    text = year

                thy_pt,thy_pt_err,thy_xs,thy_xs_err  = getLHCXS(diff=True)
                theory = ax.errorbar(thy_pt, thy_xs, xerr=thy_pt_err, linestyle='none' ,label='LHCHXSWG approx. NNLO',color='gray',lw=2)
                edges = [400.0,450.0,500,550,600,650,700,750,800]
                y_down_shade = thy_xs-thy_xs_err[1]
                y_up_shade   = thy_xs+thy_xs_err[0]
                y_up_shade   = np.r_[y_up_shade,y_up_shade[-1]]
                y_down_shade   = np.r_[y_down_shade,y_down_shade[-1]]
                shade = ax.fill_between(edges,y_down_shade, y_up_shade,step="post",hatch='///', linewidth= 0,facecolor='none')

                obs = []
                labels= []
                for binning in [[450,12000],[450, 550, 675, 12000],[300, 450, 650, 12000]]:
                    if binning ==[450,12000]: text ='%s,p T>450GeV'%year 
                    elif binning ==[450,550, 675, 12000]: text = '%s, fine-bin'%year
                    elif binning ==[300, 450, 650, 12000]: text = "%s, STXS"%year
    
                    data_pt,data_xs,data_xs_err,data_pt_err,ylabels  = getData(finalformated_table,sample,year,poi,[binning])   ## new stxs
                    obs.append( ax.errorbar(data_pt, data_xs, xerr=data_pt_err,yerr=data_xs_err, linestyle='none', marker='.', markersize=10, capsize=0,label='%s'%text) )

                    if binning==[300, 450, 650, 12000]:
                        edges = [450, 650,12000]
                        data_pt,data_xs = data_pt[1:],data_xs[1:]
                        data_xs_err = np.array([ data_xs_err[0][1:],data_xs_err[1][1:]])
                        data_pt_err = np.array([ data_pt_err[0][1:],data_pt_err[1][1:]])
                    else:
                        edges = binning
                    labels.append(text)
                    ## numbers for ratio plots
                    (ratio,ratio_err,ratio_thy,ratio_thy_err) = getintPrediction4ratio(data_pt,data_xs,data_xs_err,thy_pt,thy_xs,thy_xs_err,edges[:-1])
                    print (ratio,ratio_err,ratio_thy,ratio_thy_err)
                    ax2.errorbar(data_pt, ratio  , xerr=data_pt_err,yerr=ratio_err  , linestyle='none', marker='.', markersize=10, capsize=0)
                    ax2.errorbar(data_pt, ratio_thy, xerr=data_pt_err,yerr=ratio_thy_err, linestyle='none',color='gray',lw=2 )

                    ratio_y_down_shade = ratio_thy-ratio_thy_err[1]
                    ratio_y_up_shade   = ratio_thy+ratio_thy_err[0]
                    ratio_y_up_shade   = np.r_[ratio_y_up_shade,ratio_y_up_shade[-1]]
                    ratio_y_down_shade   = np.r_[ratio_y_down_shade,ratio_y_down_shade[-1]]

                    data_pt_up = data_pt + data_pt_err[0]
                    data_pt_down = data_pt - data_pt_err[0]
                    data_pt = np.minimum(1200,np.r_[data_pt_down, data_pt_up[-1]])

                    ax2.fill_between(data_pt, ratio_y_down_shade, ratio_y_up_shade ,step='post',hatch='///',lw=0,facecolor='none')
                
                ax.axhline(0, color='black', lw=1)
                ax.legend(title=" ")
                ax.legend(obs+[(theory,shade)], labels+['LHCHXSWG approx. NNLO'],loc=1)
                if poi =='r':
                    yTitle =  'Mu'
                else:
                    yTitle =  '$\mathrm{\Delta \sigma/\Delta p_T^H}$ (fb/GeV) '
                ax = hep.cms.cmslabel(ax, data=True, paper=False, year='136.2 $\mathrm{fb^{-1}}$')
                ax2.set_xlabel(r"$\mathrm{p_T^H}$ (GeV)", x=1, ha='right')
                ax2.set_ylabel(r"Data/prediction")
                ax.set_ylabel(r'%s'%yTitle, y=1, ha='right')
                ax.set_yscale('log')
                #plt.xlabel('p_T^H (GeV)')
                #plt.ylabel(yTitle)
                fig.savefig('./genpt/%s_%s_%s_binnings.pdf'%(sample,poi,year),bbox_inches='tight')
                fig.savefig('./genpt/%s_%s_%s_binnings.png'%(sample,poi,year),bbox_inches='tight')

if __name__ == '__main__':
    #binnings = [0,350,450,500,550,600,675,800,1200]
    #binnings = [0,100,200,300,450,500,550,600,675,800,1200]
    #binnings = [0,350,600,12000]
    mus      = []
    gen2016  = '../../analysis/genYield_6bin_v2//2016/Plots_1000pb_weighted_0.root'
    gen2017  = '../../analysis/genYield_6bin_v2//2017/Plots_1000pb_weighted_0.root'
    gen2018  = '../../analysis/genYield_6bin_v2//2018/Plots_1000pb_weighted_0.root'
    
    Fits_450 = {
        'binnings' : [450,12000],   ## must corresponds to the mu_s
        'mdf2016s' : ['cards/genpt450_minlo/2016/multidimfit.root','cards/genpt450/2016/multidimfit.root'],
        'mdf2017s' : ['cards/genpt450_minlo/2017/multidimfit.root','cards/genpt450/2017/multidimfit.root'],
        'mdf2018s' : ['cards/genpt450_minlo/2018/multidimfit.root','cards/genpt450/2018/multidimfit.root'],
        'mdfcomb'  : ['cards/genpt450_minlo/comb/multidimfit.root','cards/genpt450/comb/multidimfit.root'],
    }
    Fits_stxs = {
        'binnings' : [300,450,650,12000],
        'mdf2016s' : ['cards/genpt_stxs_minlo/2016/multidimfit.root','cards/genpt_stxs/2016/multidimfit.root'],
        'mdf2017s' : ['cards/genpt_stxs_minlo/2017/multidimfit.root','cards/genpt_stxs/2017/multidimfit.root'],
        'mdf2018s' : ['cards/genpt_stxs_minlo/2018/multidimfit.root','cards/genpt_stxs/2018/multidimfit.root'],
        'mdfcomb'  : ['cards/genpt_stxs_minlo/comb/multidimfit.root','cards/genpt_stxs/comb/multidimfit.root'],
    }
    Fits_fine = {
        'binnings' : [450,550,675,12000],
        'mdf2016s' : ['cards/genpt6_minlo/2016/multidimfit.root','cards/genpt6/2016/multidimfit.root'],
        'mdf2017s' : ['cards/genpt6_minlo/2017/multidimfit.root','cards/genpt6/2017/multidimfit.root'],
        'mdf2018s' : ['cards/genpt6_minlo/2018/multidimfit.root','cards/genpt6/2018/multidimfit.root'],
        'mdfcomb'  : ['cards/genpt6_minlo/comb/multidimfit.root','cards/genpt6/comb/multidimfit.root'],
    }
    #printTable()
    #binningPlot()
    moneyplot()
    #binningComp()
    
