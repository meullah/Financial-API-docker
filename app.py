from flask import Flask, jsonify,request
from flask_restful import Api, Resource
from flask_cors import CORS
import numpy as np
import pandas as pd
import hospitalBackEnd as H_BE
import doctorBackend as D_BE
import patientBackend as P_BE
from datetime import date
import json
import os

app = Flask(__name__)
CORS(app)
api = Api(app)
port = int(os.environ.get("PORT", 5000))

df = pd.read_csv('data.csv',parse_dates=['SERVICE_DATE','DOB']).set_index('SERVICE_DATE')
ALL_DOCTORS_IDS = df["DOC_ID"].unique().tolist()
ALL_PATIENTS_IDS = df["EMP_ID"].unique().tolist()
df_temp = df.reset_index()
YEARS_OF_DATA  = df_temp['SERVICE_DATE'].dt.year.unique().tolist()

###################################################################################
class get_all_doctors_ids(Resource):
    def get(self):
        return jsonify(ALL_DOCTORS_IDS)

class get_all_patients_ids(Resource):
    def get(self):
        return jsonify(ALL_PATIENTS_IDS)

class get_date_years(Resource):
    def get(self):
        return jsonify(YEARS_OF_DATA)
###################################################################################



def calculate_age(dtob):
    today = date.today()
    mnths = (today.month, today.day) < (dtob.month, dtob.day)
    return today.year - dtob.year - mnths

df['age'] = df.DOB.map(calculate_age)

###################################################################################
########################### HOSPITAL CHART DATA ###################################
###################################################################################

class getHospitalData(Resource):
    def get(self):
        HospitalData = {
            "yearlyTransaction" : H_BE.yearlyTransaction(df, '2019'),
            "DepartmentalExpensesData": H_BE.departmentalExpenses(df, '2018'),
            "genderChartData" : H_BE.genderChart(df, '2017'),
            "ageChartData" : H_BE.ageChart(df, '2016')
        }
        return jsonify(HospitalData)

#             ********   Gender Data  ************

class GenderData(Resource):
    def get(self,year):
        data = H_BE.genderChart(df, year)
        return jsonify(data)

#             ********   Age Group Data  ************

class AgeGroupData(Resource):
    def get(self,year):
        data = H_BE.ageChart(df, year)
        return jsonify(data)
   

#     ********  Departmental Epenses  Data  ************

class DepartmentalExpensesData(Resource):
    def get(self,year):
        data = {
            "dept_exp_data": H_BE.departmentalExpenses(df, year)
        }
        return jsonify(data)
#     ********  Yearly Transaction  Data  ************
class YearlyTransactionData(Resource):
    def get(self,year):
        data = { "yearlyTransaction" : H_BE.yearlyTransaction(df, year),
                "Anomaly" : [1,1,1,1,1,1,2,3,0,0,1,2]}
        return jsonify(data)

class Home(Resource):
    def get(self):
        return jsonify("Hello Word!!")


###################################################################################
########################### DOCTOR'S CHART DATA ###################################
###################################################################################

class DoctorsEarlyRecord(Resource):
    def get(self,year=2018,doc_id=551):
        x = D_BE.docMonthlyPatientVisits(df,year,doc_id)
        return jsonify(x)
               
class DoctorPatientGenderAgeVisits(Resource):
    def get(self,year,doc_id):
        x = D_BE.docPatientGenderAgeVisits(df,year,doc_id)
        return jsonify(x)
        
class DoctorPatientGenderVisits(Resource):
    def get(self,year,doc_id):
        x = D_BE.docPatientGenderVisits(df,year,doc_id)
        return jsonify(x)


###################################################################################
############ Hospital Amount Transaction Prediction CHART DATA ####################
###################################################################################

class Hospital_TransactionAmmount_Prediction(Resource):
    def get(self,value): # value number of months to be predicted
        x = H_BE.predict(values=value)
        x = x["AMOUNT"].values.tolist()
        data = {"pridicted_values" : x }
        return jsonify(data)

class DoctorBubbleChartData(Resource):
    def get(self,doc_id):
        mydf = D_BE.doc_AgevsService(doc_id)
        data = {
                "age_group" : mydf["Age Group"].values.tolist(),
                "service" : mydf["Service"].values.tolist(),
                "frequency" : mydf["Count"].values.tolist()
            }
        return (data)

class PatientBubbleChartData(Resource):
    def get(self,patient_id):
        mydf = P_BE.patient_DocvsService(patient_id)
        data = {
                "doc_id" : mydf["DOC_ID"].values.tolist(),
                "service_id" : mydf["Service_ID"].values.tolist(),
                "frequency" : mydf["Count"].values.tolist()
            }
        return json.dumps(data)


api.add_resource(get_all_doctors_ids,'/doctors_ids')
api.add_resource(get_all_patients_ids,'/patients_ids')
api.add_resource(get_date_years,'/dateyears')


api.add_resource(getHospitalData,'/hospitalData')
api.add_resource(GenderData,'/genderData/year/<year>')
api.add_resource(AgeGroupData,'/ageGroupData/year/<year>')
api.add_resource(DepartmentalExpensesData,'/departmentalExpensesData/year/<year>')
api.add_resource(YearlyTransactionData,'/yearlyTransactionData/year/<year>')

api.add_resource(DoctorsEarlyRecord,'/doctorsPatientEarlyRecord/year/<int:year>/doc_id/<int:doc_id>')
api.add_resource(DoctorPatientGenderVisits,'/doctorsPatientGenderRecord/year/<int:year>/doc_id/<int:doc_id>')
api.add_resource(DoctorPatientGenderAgeVisits,'/doctorsPatientGenderAgeRecord/year/<int:year>/doc_id/<int:doc_id>')

api.add_resource(Hospital_TransactionAmmount_Prediction,'/hospitalYearlyPrediction/<int:value>')
api.add_resource(DoctorBubbleChartData,"/doctorbubblechart/doc_id/<int:doc_id>")
api.add_resource(PatientBubbleChartData,"/patientbubblechart/patient_id/<string:patient_id>")


api.add_resource(Home,'/')

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True,port=port)


