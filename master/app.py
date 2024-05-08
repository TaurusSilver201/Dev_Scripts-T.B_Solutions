import sys
import numpy as np
import pdb
sys.path.append("../")

from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
import kwbreaker.app as kwapp
import kwbreaker.utils as kwutils
import pandas as pd
import TM.app as tmapp
import TM.utils as tmutils
import OC.app as ocapp
import OC.utils as ocutils
import latest_noprofits.app_update as noprofitsapp
import crunchbase.app as crunchbaseapp
import crunchbase.utils as crunchbaseutils


def main():
    kwutils.TERMS_FILE = "domains.txt"
    kw_df = pd.DataFrame(kwapp.main(), columns=["kwbreaker-terms", "kwbreaker-final_terms", "kwbreaker-scores"])
    kw_df.loc[kw_df["kwbreaker-terms"].str.contains(".com") | kw_df["kwbreaker-terms"].str.contains(".net"), "kwbreaker-final_terms"].to_csv("dot_com_dot_net_terms.txt", index=False, header=False)
    kw_df.loc[kw_df["kwbreaker-terms"].str.contains(".org"), "kwbreaker-final_terms"].to_csv("dot_org_terms.txt", index=False, header=False)
    dot_com_dot_net_len = len(kw_df.loc[kw_df["kwbreaker-terms"].str.contains(".com") | kw_df["kwbreaker-terms"].str.contains(".net"), "kwbreaker-final_terms"].index)
    dot_org_len = len(kw_df.loc[kw_df["kwbreaker-terms"].str.contains(".org"), "kwbreaker-final_terms"].index)
    # print("len ", dot_com_dot_net_len, dot_org_len)
    # tmutils.TERMS_FILE = 'dot_com_dot_net_terms.txt'
    # nonprofitutils.TERMS_FILE = "dot_org_terms.txt"

    with ProcessPoolExecutor(max_workers=3) as executor:
        #tm_futures = None
        oc_nonprofits_0_futures = None
        cb_crunchbase_0_futures = None
        if dot_com_dot_net_len>0:
            # tm_futures = executor.submit(tmapp.main, {"TERMS_FILE": 'dot_com_dot_net_terms.txt'})
            oc_nonprofits_0_futures = executor.submit(ocapp.main, {"nonprofits_only": 0, "TERMS_FILE": 'dot_com_dot_net_terms.txt'})
            cb_crunchbase_0_futures = executor.submit(crunchbaseapp.main, {"crunchbase_only": 0, "TERMS_FILE": 'dot_com_dot_net_terms.txt'})

        oc_nonprofits_1_futures = None
        nonprofits_futures = None

        if dot_org_len>0:
            oc_nonprofits_1_futures = executor.submit(ocapp.main, {"nonprofits_only": 1, "TERMS_FILE": 'dot_org_terms.txt'})
            nonprofits_futures = executor.submit(noprofitsapp.main, {"TERMS_FILE": 'dot_org_terms.txt'})
        #tm_result = []
        #if tm_futures:
        #    tm_result = tm_futures.result()

        oc_nonprofits_0_result = []
        if oc_nonprofits_0_futures:
            oc_nonprofits_0_result = oc_nonprofits_0_futures.result()
        
        oc_nonprofits_1_result = []
        if oc_nonprofits_1_futures:
            oc_nonprofits_1_result = oc_nonprofits_1_futures.result()
        
        nonprofits_result = []
        if nonprofits_futures:
            nonprofits_result = nonprofits_futures.result()
            
            
        #crunchbase implementation
        cb_crunchbase_0_result = []
        if cb_crunchbase_0_futures:
            cb_crunchbase_0_result = cb_crunchbase_0_futures.result()
        

        #kw_df["TM-TM"] = ""
        #if len(tm_result)>0:
        #    kw_df.loc[kw_df["kwbreaker-terms"].str.contains(".com") | kw_df["kwbreaker-terms"].str.contains(".net"), "TM-TM"] = tm_result

        kw_df["CB|NP"] = ""
        kw_df["OC-OC_Score"] = ""
        kw_df["OC-OC1"] = ""
        kw_df["OC-OC2"] = ""
        kw_df["OC-OC_US"] = ""
        #kw_df["NP-NP"] = ""
        
        if len(oc_nonprofits_0_result)>0:
            #kw_df.loc[kw_df["kwbreaker-terms"].str.contains(".com") | kw_df["kwbreaker-terms"].str.contains(".net"), ["CB|NP", "OC-OC_Score", "OC-OC1", "OC-OC2", "OC-OC_US"]] = [tmp[1:5] for tmp in oc_nonprofits_0_result]
            cb_columns = ['kwbreaker-final_terms', 'OC-OC_Score', 'OC-OC1', 'OC-OC2', 'OC-OC_US']
            cb_df = pd.DataFrame([tmp[0:5] for tmp in oc_nonprofits_0_result], columns=cb_columns)
            kw_df.loc[kw_df['kwbreaker-terms'].str.contains('.net|.com'), ['OC-OC_Score', 'OC-OC1', 'OC-OC2', 'OC-OC_US']] =[tmp[1:5] for tmp in oc_nonprofits_0_result]



        if len(oc_nonprofits_1_result)>0:
            cb_columns = ['kwbreaker-final_terms', 'OC-OC_Score', 'OC-OC1', 'OC-OC2', 'OC-OC_US']
            cb_df = pd.DataFrame([tmp[0:5] for tmp in oc_nonprofits_1_result], columns=cb_columns)
            kw_df.loc[kw_df['kwbreaker-terms'].str.contains('.org'), ['OC-OC_Score', 'OC-OC1', 'OC-OC2', 'OC-OC_US']] =[tmp[1:5] for tmp in oc_nonprofits_1_result]


        if len(cb_crunchbase_0_result)>0:
            #kw_df.loc[kw_df['kwbreaker-terms'].str.contains('.com|.net'), ['kwbreaker-final_terms','CB|NP']] = [tmp for tmp in cb_crunchbase_0_result]
            mapping_list = [tmp for tmp in cb_crunchbase_0_result]
            mapping_dict = {item[0]: item[1] for item in mapping_list}
            kw_df.loc[kw_df['kwbreaker-terms'].str.contains('.com|.net', case=False, na=False), 'CB|NP'] =  kw_df.apply(lambda row, mapping_dict=mapping_dict: mapping_dict.get(row['kwbreaker-final_terms']) if ('.com' in row['kwbreaker-terms'] or '.net' in row['kwbreaker-terms']) else row['CB|NP'], axis=1)
            #kw_df['CB|NP'] = kw_df['CB|NP'].astype('Int64')
        
        if len(nonprofits_result)>0:
            #kw_df.loc[kw_df['kwbreaker-terms'].str.contains('.org'), ['kwbreaker-final_terms','CB|NP']] = [tmp for tmp in nonprofits_result]
            mapping_list = [tmp for tmp in nonprofits_result]
            mapping_dict = {item[0]: item[1] for item in mapping_list}
            kw_df.loc[kw_df['kwbreaker-terms'].str.contains('.org', case=False, na=False), 'CB|NP'] =  kw_df.apply(lambda row, mapping_dict=mapping_dict: mapping_dict.get(row['kwbreaker-final_terms']) if '.org' in row['kwbreaker-terms'] else row['CB|NP'], axis=1)

               
        
        
        today = datetime.today()
        del kw_df["kwbreaker-final_terms"]
        kw_df.replace({0: None})
        #kw_df.replace(0, np.nan, inplace=True)
        # kw_df.replace("0", "", inplace=True)
        kw_df.to_csv(f"master_report_{today.strftime('%Y%d%m_%H%M%S')}.csv", index=False)


if __name__ == "__main__":
    main()
