import wbgapi as wb
from datetime import datetime, date
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller

def model(id, first_year, last_year, forcast_years = 3):

    def todate(x):
        date_str = x[2:]
        date_format = "%Y"  # "YR" represents year and "%b" represents abbreviated month
        datetime_obj = datetime.strptime(date_str, date_format)
        return datetime_obj

    ECONOMY = wb.data.DataFrame(['NY.GDP.MKTP.CD', 'NE.EXP.GNFS.CD', 'NE.IMP.GNFS.CD', 'SL.UEM.TOTL.ZS'], id, range(first_year, last_year)).transpose().reset_index().rename(columns={'index':'years'})
    
    if ECONOMY['NY.GDP.MKTP.CD'].isna().sum() != 0:
        mean_ECONOMY = ECONOMY['NY.GDP.MKTP.CD'].mean()
        ECONOMY['NY.GDP.MKTP.CD'].fillna(mean_ECONOMY, inplace=True)

    if ECONOMY['NE.EXP.GNFS.CD'].isna().sum() != 0:
        mean_ECONOMY = ECONOMY['NE.EXP.GNFS.CD'].mean()
        ECONOMY['NE.EXP.GNFS.CD'].fillna(mean_ECONOMY, inplace=True)

    if ECONOMY['NE.IMP.GNFS.CD'].isna().sum() != 0:
        mean_ECONOMY = ECONOMY['NE.IMP.GNFS.CD'].mean()
        ECONOMY['NE.IMP.GNFS.CD'].fillna(mean_ECONOMY, inplace=True)

    if ECONOMY['SL.UEM.TOTL.ZS'].isna().sum() != 0:
        mean_ECONOMY = ECONOMY['SL.UEM.TOTL.ZS'].mean()
        ECONOMY['SL.UEM.TOTL.ZS'].fillna(mean_ECONOMY, inplace=True)
        
    ECONOMY['years'] = ECONOMY['years'].apply(todate)
    ECONOMY['NY.GDP.MKTP.CD']  = ECONOMY['NY.GDP.MKTP.CD'].apply(lambda x: int(x))
    ECONOMY['NE.EXP.GNFS.CD']  = ECONOMY['NE.EXP.GNFS.CD'].apply(lambda x: int(x))
    ECONOMY['NE.IMP.GNFS.CD']  = ECONOMY['NE.IMP.GNFS.CD'].apply(lambda x: int(x))

    def d_value(series):
        p = 1
        ts_stationary = series
        d = 0

        while p > 0.05:
            result = adfuller(ts_stationary)
            p = result[1]

            if p > 0.05:
                ts_stationary = ts_stationary.diff().dropna()
                d+=1
            else:
                break
        return d
    
    GDP_d = d_value(ECONOMY['NY.GDP.MKTP.CD'])
    EXP_d = d_value(ECONOMY['NE.EXP.GNFS.CD'])
    IMP_d = d_value(ECONOMY['NE.IMP.GNFS.CD'])
    UMP_d = d_value(ECONOMY['SL.UEM.TOTL.ZS'])

    GDP_model = ARIMA(ECONOMY['NY.GDP.MKTP.CD'], order=(1, GDP_d, 2))
    EXP_model = ARIMA(ECONOMY['NE.EXP.GNFS.CD'], order=(1, EXP_d, 2))
    IMP_model = ARIMA(ECONOMY['NE.IMP.GNFS.CD'], order=(1, IMP_d, 2))
    UMP_model = ARIMA(ECONOMY['SL.UEM.TOTL.ZS'], order=(1, UMP_d, 2))

    GDP_model_fit = GDP_model.fit()
    EXP_model_fit = EXP_model.fit()
    IMP_model_fit = IMP_model.fit()
    UMP_model_fit = UMP_model.fit()

    GDP_predictions = GDP_model_fit.predict(start=len(ECONOMY['NY.GDP.MKTP.CD']), end=len(ECONOMY['NY.GDP.MKTP.CD']) + forcast_years)
    EXP_predictions = EXP_model_fit.predict(start=len(ECONOMY['NE.EXP.GNFS.CD']), end=len(ECONOMY['NE.EXP.GNFS.CD']) + forcast_years)
    IMP_predictions = IMP_model_fit.predict(start=len(ECONOMY['NE.IMP.GNFS.CD']), end=len(ECONOMY['NE.IMP.GNFS.CD']) + forcast_years)
    UMP_predictions = UMP_model_fit.predict(start=len(ECONOMY['SL.UEM.TOTL.ZS']), end=len(ECONOMY['SL.UEM.TOTL.ZS']) + forcast_years)

    def pred_df(predictions):
        df = pd.DataFrame(predictions)
        str_forcast_start = str(last_year)
        str_forcast_end = str(last_year + forcast_years)
        df['years'] = pd.date_range(start=pd.to_datetime(str_forcast_start), end=pd.to_datetime(str_forcast_end), freq='YS')
        df['predicted_mean'] = df['predicted_mean'].apply(lambda x: int(x))
        return df
    
    GDP_df = pred_df(GDP_predictions)
    EXP_df = pred_df(EXP_predictions)
    IMP_df = pred_df(IMP_predictions)
    UMP_df = pred_df(UMP_predictions)

    return ECONOMY, GDP_df, EXP_df, IMP_df, UMP_df
