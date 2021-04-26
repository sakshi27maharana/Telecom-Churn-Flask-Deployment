# Telecom-Churn-Flask-Deployment
Telecom-Churn-Case-Study : Flask Deployment ( Running on http://localhost:5000/ )

### Business Objective
The dataset contains customer-level information for a span of four consecutive months - June, July, August and September. The months are encoded as 6, 7, 8 and 9, respectively. The business objective is to predict the churn in the last (i.e. the ninth) month using the data (features) from the first three months. To do this task well, understanding the typical customer behaviour during churn will be helpful. In this case, since you are working over a four-month window, the first two months are the ‘good’ phase, the third month is the ‘action’ phase, while the fourth month is the ‘churn’ phase.

### Project Data
1. We have been provided with the 2008 year data of Telecom Industry, in the form of ".csv" file. The dataset contains customer-level information for a span of four consecutive months(June, July, August and September).
2. The data dictionary contains meanings of abbreviations.

### Folders/Files used
1. model : contains saved model which was used while coding
2. output : store the sample output snapshot here
3. templates : store the index.html file for the front-end coding
4. app.py : contains code for flask application
5. request.py : contains request generation code from the application
6. preprocess.py : contains preprocessing step from the dataset needed to have filtered churn data
7. Data+Dictionary-+Telecom+Churn+Case+Study.xlsx : contains the details of the columns used in the dataset
