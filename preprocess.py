# import libraries
import pandas as pd
import numpy as np
from fancyimpute import MICE
from sklearn.model_selection import train_test_split

# read data
tchurn = pd.read_csv("telecom_churn_data.csv")

# Sample Data for Preprocessing
tchurn = tchurn.head(10)
# create backup of data
original = tchurn.copy()

# create column name list by types of columns
id_cols = ['mobile_number', 'circle_id']

date_cols = ['last_date_of_month_6',
             'last_date_of_month_7',
             'last_date_of_month_8',
             'last_date_of_month_9',
             'date_of_last_rech_6',
             'date_of_last_rech_7',
             'date_of_last_rech_8',
             'date_of_last_rech_9',
             'date_of_last_rech_data_6',
             'date_of_last_rech_data_7',
             'date_of_last_rech_data_8',
             'date_of_last_rech_data_9'
            ]

cat_cols =  ['night_pck_user_6',
             'night_pck_user_7',
             'night_pck_user_8',
             'night_pck_user_9',
             'fb_user_6',
             'fb_user_7',
             'fb_user_8',
             'fb_user_9'
            ]

num_cols = [column for column in tchurn.columns if column not in id_cols + date_cols + cat_cols]

# Impute missing values
# i) Imputing with zeroes
# some recharge columns have minimum value of 1 while some don't
recharge_cols = ['total_rech_data_6', 'total_rech_data_7', 'total_rech_data_8', 'total_rech_data_9',
                 'count_rech_2g_6', 'count_rech_2g_7', 'count_rech_2g_8', 'count_rech_2g_9',
                 'count_rech_3g_6', 'count_rech_3g_7', 'count_rech_3g_8', 'count_rech_3g_9',
                 'max_rech_data_6', 'max_rech_data_7', 'max_rech_data_8', 'max_rech_data_9',
                 'av_rech_amt_data_6', 'av_rech_amt_data_7', 'av_rech_amt_data_8', 'av_rech_amt_data_9',
                 ]

# It is also observed that the recharge date and the recharge value are missing together which means the customer
# didn't recharge
tchurn.loc[tchurn.total_rech_data_6.isnull() & tchurn.date_of_last_rech_data_6.isnull(), ["total_rech_data_6", "date_of_last_rech_data_6"]].head(20)

# In the recharge variables where minumum value is 1, we can impute missing values with zeroes since it means customer
# didn't recharge their numbere that month.
# create a list of recharge columns where we will impute missing values with zeroes
zero_impute = ['total_rech_data_6', 'total_rech_data_7', 'total_rech_data_8', 'total_rech_data_9',
        'av_rech_amt_data_6', 'av_rech_amt_data_7', 'av_rech_amt_data_8', 'av_rech_amt_data_9',
        'max_rech_data_6', 'max_rech_data_7', 'max_rech_data_8', 'max_rech_data_9'
       ]

# impute missing values with 0
tchurn[zero_impute] = tchurn[zero_impute].apply(lambda x: x.fillna(0))

# drop id and date columns
tchurn = tchurn.drop(id_cols + date_cols, axis=1)

# ii) Replace NaN values in categorical variables
# We will replace missing values in the categorical values with '-1' where '-1' will be a new category.
# replace missing values with '-1' in categorical columns
tchurn[cat_cols] = tchurn[cat_cols].apply(lambda x: x.fillna(-1))

# iii) Drop variables with more than a given threshold of missing values
initial_cols = churn.shape[1]
MISSING_THRESHOLD = 0.7
include_cols = list(tchurn.apply(lambda column: True if column.isnull().sum()/tchurn.shape[0] < MISSING_THRESHOLD else False))
drop_missing = pd.DataFrame({'features':tchurn.columns , 'include': include_cols})
drop_missing.loc[drop_missing.include == True,:]

# drop columns
tchurn = tchurn.loc[:, include_cols]

dropped_cols = tchurn.shape[1] - initial_cols

# iv) imputing using MICE
# install fancyimpute package using [this](https://github.com/iskandr/fancyimpute) link and following the install instructions
churn_cols = tchurn.columns

# using MICE technique to impute missing values in the rest of the columns
churn_imputed = MICE(n_imputations=1).complete(tchurn)

# convert imputed numpy array to pandas dataframe
tchurn = pd.DataFrame(churn_imputed, columns=churn_cols)

# # filter high-value customers
# ### calculate total data recharge amount

# calculate the total data recharge amount for June and July --> number of recharges * average recharge amount
tchurn['total_data_rech_6'] = tchurn.total_rech_data_6 * tchurn.av_rech_amt_data_6
tchurn['total_data_rech_7'] = tchurn.total_rech_data_7 * tchurn.av_rech_amt_data_7

# calculate total recharge amount for June and July --> call recharge amount + data recharge amount
tchurn['amt_data_6'] = tchurn.total_rech_amt_6 + tchurn.total_data_rech_6
tchurn['amt_data_7'] = tchurn.total_rech_amt_7 + tchurn.total_data_rech_7

# calculate average recharge done by customer in June and July
tchurn['av_amt_data_6_7'] = (tchurn.amt_data_6 + tchurn.amt_data_7)/2

# retain only those customers who have recharged their mobiles with more than or equal to 70th percentile amount
filter_tchurn = tchurn.loc[tchurn.av_amt_data_6_7 >= tchurn.av_amt_data_6_7.quantile(0.7), :]
filter_tchurn = filter_tchurn.reset_index(drop=True)

# delete variables created to filter high-value customers
filter_tchurn = filter_tchurn.drop(['total_data_rech_6', 'total_data_rech_7',
                                      'amt_data_6', 'amt_data_7', 'av_amt_data_6_7'], axis=1)

# We're left with 30,001 rows after selecting the customers who have provided recharge value of more than or equal to the recharge value of the 70th percentile customer.
# # derive churn
# calculate total incoming and outgoing minutes of usage
filter_tchurn['total_calls_mou_9'] = filter_tchurn.total_ic_mou_9 + filter_tchurn.total_og_mou_9

# calculate 2g and 3g data consumption
filter_tchurn['total_internet_mb_9'] =  filter_tchurn.vol_2g_mb_9 + filter_tchurn.vol_3g_mb_9

# create churn variable: those who have not used either calls or internet in the month of September are customers who have churned

# 0 - not churn, 1 - churn
filter_tchurn['churn'] = churn_filtered.apply(lambda row: 1 if (row.total_calls_mou_9 == 0 and row.total_internet_mb_9 == 0) else 0, axis=1)

# delete derived variables
filter_tchurn = filter_tchurn.drop(['total_calls_mou_9', 'total_internet_mb_9'], axis=1)

# change data type to category
filter_tchurn.churn = filter_tchurn.churn.astype("category")

# # Calculate difference between 8th and previous months
# Let's derive some variables. The most important feature, in this situation, can be the difference between the 8th month and the previous months. The difference can be in patterns such as usage difference or recharge value difference. Let's calculate difference variable as the difference between 8th month and the average of 6th and 7th month.

filter_tchurn['arpu_diff'] = filter_tchurn.arpu_8 - ((filter_tchurn.arpu_6 + filter_tchurn.arpu_7)/2)
filter_tchurn['onnet_mou_diff'] = filter_tchurn.onnet_mou_8 - ((filter_tchurn.onnet_mou_6 + filter_tchurn.onnet_mou_7)/2)
filter_tchurn['offnet_mou_diff'] = filter_tchurn.offnet_mou_8 - ((filter_tchurn.offnet_mou_6 + filter_tchurn.offnet_mou_7)/2)
filter_tchurn['roam_ic_mou_diff'] = filter_tchurn.roam_ic_mou_8 - ((filter_tchurn.roam_ic_mou_6 + filter_tchurn.roam_ic_mou_7)/2)
filter_tchurn['roam_og_mou_diff'] = filter_tchurn.roam_og_mou_8 - ((filter_tchurn.roam_og_mou_6 + filter_tchurn.roam_og_mou_7)/2)
filter_tchurn['loc_og_mou_diff'] = filter_tchurn.loc_og_mou_8 - ((filter_tchurn.loc_og_mou_6 + filter_tchurn.loc_og_mou_7)/2)
filter_tchurn['std_og_mou_diff'] = filter_tchurn.std_og_mou_8 - ((filter_tchurn.std_og_mou_6 + filter_tchurn.std_og_mou_7)/2)
filter_tchurn['isd_og_mou_diff'] = filter_tchurn.isd_og_mou_8 - ((filter_tchurn.isd_og_mou_6 + filter_tchurn.isd_og_mou_7)/2)
filter_tchurn['spl_og_mou_diff'] = filter_tchurn.spl_og_mou_8 - ((filter_tchurn.spl_og_mou_6 + filter_tchurn.spl_og_mou_7)/2)
filter_tchurn['total_og_mou_diff'] = filter_tchurn.total_og_mou_8 - ((filter_tchurn.total_og_mou_6 + filter_tchurn.total_og_mou_7)/2)
filter_tchurn['loc_ic_mou_diff'] = filter_tchurn.loc_ic_mou_8 - ((filter_tchurn.loc_ic_mou_6 + filter_tchurn.loc_ic_mou_7)/2)
filter_tchurn['std_ic_mou_diff'] = filter_tchurn.std_ic_mou_8 - ((filter_tchurn.std_ic_mou_6 + filter_tchurn.std_ic_mou_7)/2)
filter_tchurn['isd_ic_mou_diff'] = filter_tchurn.isd_ic_mou_8 - ((filter_tchurn.isd_ic_mou_6 + filter_tchurn.isd_ic_mou_7)/2)
filter_tchurn['spl_ic_mou_diff'] = filter_tchurn.spl_ic_mou_8 - ((filter_tchurn.spl_ic_mou_6 + filter_tchurn.spl_ic_mou_7)/2)
filter_tchurn['total_ic_mou_diff'] = filter_tchurn.total_ic_mou_8 - ((filter_tchurn.total_ic_mou_6 + filter_tchurn.total_ic_mou_7)/2)
filter_tchurn['total_rech_num_diff'] = filter_tchurn.total_rech_num_8 - ((filter_tchurn.total_rech_num_6 + filter_tchurn.total_rech_num_7)/2)
filter_tchurn['total_rech_amt_diff'] = filter_tchurn.total_rech_amt_8 - ((filter_tchurn.total_rech_amt_6 + filter_tchurn.total_rech_amt_7)/2)
filter_tchurn['max_rech_amt_diff'] = filter_tchurn.max_rech_amt_8 - ((filter_tchurn.max_rech_amt_6 + filter_tchurn.max_rech_amt_7)/2)
filter_tchurn['total_rech_data_diff'] = filter_tchurn.total_rech_data_8 - ((filter_tchurn.total_rech_data_6 + filter_tchurn.total_rech_data_7)/2)
filter_tchurn['max_rech_data_diff'] = filter_tchurn.max_rech_data_8 - ((filter_tchurn.max_rech_data_6 + filter_tchurn.max_rech_data_7)/2)
filter_tchurn['av_rech_amt_data_diff'] = filter_tchurn.av_rech_amt_data_8 - ((filter_tchurn.av_rech_amt_data_6 + filter_tchurn.av_rech_amt_data_7)/2)
filter_tchurn['vol_2g_mb_diff'] = filter_tchurn.vol_2g_mb_8 - ((filter_tchurn.vol_2g_mb_6 + filter_tchurn.vol_2g_mb_7)/2)
filter_tchurn['vol_3g_mb_diff'] = filter_tchurn.vol_3g_mb_8 - ((filter_tchurn.vol_3g_mb_6 + filter_tchurn.vol_3g_mb_7)/2)


# ## delete columns that belong to the churn month (9th month)
# delete all variables relating to 9th month
filter_tchurn = filter_tchurn.filter(regex='[^9]$', axis=1)

# extract all names that end with 9
col_9_names = tchurn.filter(regex='9$', axis=1).columns

# update num_cols and cat_cols column name list
cat_cols = [col for col in cat_cols if col not in col_9_names]
cat_cols.append('churn')
num_cols = [col for col in filter_tchurn.columns if col not in cat_cols]

# change columns types
filter_tchurn[num_cols] = filter_tchurn[num_cols].apply(pd.to_numeric)
filter_tchurn[cat_cols] = filter_tchurn[cat_cols].apply(lambda column: column.astype("category"), axis=0)

# create plotting functions
def data_type(variable):
    if variable.dtype == np.int64 or variable.dtype == np.float64:
        return 'numerical'
    elif variable.dtype == 'category':
        return 'categorical'

pd.crosstab(filter_tchurn.churn, filter_tchurn.night_pck_user_8, normalize='columns')*100

pd.crosstab(filter_tchurn.churn, filter_tchurn.sachet_3g_8)


# ### Cap outliers in all numeric variables with k-sigma technique
def cap_outliers(array, k=3):
    upper_limit = array.mean() + k*array.std()
    lower_limit = array.mean() - k*array.std()
    array[array<lower_limit] = lower_limit
    array[array>upper_limit] = upper_limit
    return array

# example of capping
sample_array = list(range(100))

# add outliers to the data
sample_array[0] = -9999
sample_array[99] = 9999

# cap outliers
sample_array = np.array(sample_array)
# cap outliers in the numeric columns
filter_tchurn[num_cols] = filter_tchurn[num_cols].apply(cap_outliers, axis=0)


# # Modelling
# i) Making predictions
# Preprocessing data

# change churn to numeric
filter_tchurn['churn'] = pd.to_numeric(filter_tchurn['churn'])

# Train Test split
# divide data into train and test
X = filter_tchurn.drop("churn", axis = 1)
y = filter_tchurn.churn
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.8, random_state = 4, stratify = y)

#reshape
X_train = X_train.values.reshape(-1, 1)
X_test = X_test.values.reshape(-1, 1)

# Aggregating the categorical columns
train = pd.concat([X_train, y_train], axis=1)

# aggregate the categorical variables
train.groupby('night_pck_user_6').tchurn.mean()
train.groupby('night_pck_user_7').tchurn.mean()
train.groupby('night_pck_user_8').churn.mean()
train.groupby('fb_user_6').tchurn.mean()
train.groupby('fb_user_7').tchurn.mean()
train.groupby('fb_user_8').tchurn.mean()

# replace categories with aggregated values in each categorical column
mapping = {'night_pck_user_6' : {-1: 0.099165, 0: 0.066797, 1: 0.087838},
           'night_pck_user_7' : {-1: 0.115746, 0: 0.055494, 1: 0.051282},
           'night_pck_user_8' : {-1: 0.141108, 0: 0.029023, 1: 0.016194},
           'fb_user_6'        : {-1: 0.099165, 0: 0.069460, 1: 0.067124},
           'fb_user_7'        : {-1: 0.115746, 0: 0.059305, 1: 0.055082},
           'fb_user_8'        : {-1: 0.141108, 0: 0.066887, 1: 0.024463}
          }

X_train.replace(mapping, inplace = True)
X_test.replace(mapping, inplace = True)

# check data type of categorical columns - make sure they are numeric
X_train[[col for col in cat_cols if col not in ['churn']]].info()


# Feature Importance
# predictors
top_features = ['total_ic_mou_8', 'total_rech_amt_diff', 'total_og_mou_8', 'arpu_8', 'roam_ic_mou_8', 'roam_og_mou_8',
                'std_ic_mou_8', 'av_rech_amt_data_8', 'std_og_mou_8']

X_train = X_train[top_features]
X_test = X_test[top_features]

print(X_test)
