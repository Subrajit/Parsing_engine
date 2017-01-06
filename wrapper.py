"""
Function to wrap all functions
"""

"""
Load libraries
"""
import argparse
import csv
import functools
import glob
import logging
import os
import re
import sys
import pandas as pd
reload(sys)
sys.setdefaultencoding('utf8')
import pandas as pd
import pdfminer
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO		
from xlrd import open_workbook
import pdftables_api

"""
Read CSV files 
"""
KeywordsPG = pd.read_csv("C:\\Users\\tmehta\\Desktop\\Subrajit\\Axis Bank\\CV parsing\\Data_Masters\\MastersBOW.csv")
KeywordsGrad = pd.read_csv("C:\\Users\\tmehta\\Desktop\\Subrajit\\Axis Bank\\CV parsing\\Data_Masters\\BachelorsBOW.csv")
KeywordsPG_SK = pd.read_csv("C:\\Users\\tmehta\\Desktop\\Subrajit\\Axis Bank\\CV parsing\\Data_Masters\\MastersBOW_SK.csv")
KeywordsGrad_SK = pd.read_csv("C:\\Users\\tmehta\\Desktop\\Subrajit\\Axis Bank\\CV parsing\\Data_Masters\\BachelorsBOW_SK.csv")


KeywordsHSC=pd.read_csv('C:/Users/tmehta/Desktop/Subrajit/Axis Bank/CV parsing/Data_Masters/HSC.csv')
KeywordsSSC=pd.read_csv('C:/Users/tmehta/Desktop/Subrajit/Axis Bank/CV parsing/Data_Masters/SSC.csv')

"""
Read all pdf files from the working directory
"""


"""
define working directory
"""
import os 
os.chdir("C:/Users/tmehta/Desktop/Subrajit/Axis Bank/CV parsing/Axis")
#os.chdir("C:/Users/tmehta/Desktop/Subrajit/Axis Bank/Tabular")

import os.path
i=1
filesname= []
for dirpath, dirnames, filenames in os.walk("."):
	for filename in [f for f in filenames if f.endswith(".pdf")]:
		print i
		i=i+1
		try:
			filesname.extend([str(os.path.join(dirpath, filename))])
		except:
			None
		print os.path.join(dirpath, filename)

for root, directories, files in os.walk("C:/Users/tmehta/Desktop/Subrajit/Axis Bank/CV parsing/Axis"):
	for filename in files:
		# Join the two strings in order to form the full filepath.
		filepath = os.path.join(root, filename)
		filesname.append(filepath)
			

###Declare the master dataframe
columns= ["Name_Path","Email_Address","Mobile_Number","YOB","Address_PIN","District","State","Is_Post_Graduate","Is_Graduate","Post_Graduate_details","Graduate_details","Post_Graduate_College","Graduate_College","PG_percentage","Graduate_percentage","PG_Univ_Tier","Graduate_Univ_Tier","Banking_Role","Circle","Region","City","excel","is_ed_table"]	

df_master= pd.DataFrame(columns= columns)


for i in range(1,100): 		
	##read the exact file name to pass to reading xls file		
	try:
		input_pdf_path= filesname[i]
		split_path= input_pdf_path.split('\\')
		length= len(split_path)
		split_path= split_path[length-1]
		regex= re.compile("(.+?)"+r".pdf")
		result = re.search(regex,split_path ) 
		file_title=result.group(1)
	except:
		continue
		

	###Declare empty variables
	Name_Path,Email_Address,Mobile_Number,YOB,Address_PIN,District,State,Is_Post_Graduate,Is_Graduate,Post_Graduate_details,Graduate_details,Post_Graduate_College,Graduate_College,PG_percentage,Graduate_percentage,PG_Univ_Tier,Graduate_Univ_Tier,Banking_Role,Circle,Region,City="","","","","","","","","","","","","","","","","","","","",""

	###return name, mobile number and pin code
	string_to_search= convert_pdf_to_txt(input_pdf_path)
	Name_Path= filesname[i]
	Mobile_Number=check_phone_number(string_to_search)
	Email_Address= check_email(string_to_search)
	##print output
	Name_Path,Mobile_Number,Email_Address

	##return pin number address and circle
	Address_PIN=return_pin_location(string_to_search,1)
	District=return_pin_location(string_to_search,2)
	State=return_pin_location(string_to_search,3)
	##print output
	Address_PIN,District,State

	##return year of birth
	YOB= return_year_of_birth(string_to_search)
	YOB
	###calling functions for education
	check_for_ed_table= fun_istable(string_to_search)

	###extract PG, UG and percentage values
	Is_Post_Graduate=fun_isPG(string_to_search)[0]
	Post_Graduate_details= fun_isPG(string_to_search)[1]
	Is_Graduate=fun_isGrad(string_to_search)[0]
	Graduate_details= fun_isGrad(string_to_search)[1]
	
	#check for education table presense and pass to dataframe
	if check_for_ed_table==0:
		is_ed_table="No"
	else:
		is_ed_table="Yes"
	if Is_Post_Graduate=="Yes":
		PG_percentage= fun_get_percentage(string_to_search,Post_Graduate_details)
	if Is_Graduate=="Yes":	
		Graduate_percentage= fun_get_percentage(string_to_search,Graduate_details)
		


	###check for table for percentage values
	excel="No"
	try:
		wb = open_workbook('C:/Users/tmehta/Desktop/Subrajit/Axis Bank/Tableanalysis/'+file_title+'.xlsx')
		sheets = wb.sheet_names()
		sheet = wb.sheet_by_name(sheets[0])
		excel="Yes"
	except:
		None
		#c = pdftables_api.Client('jk8vehn938si')
		#filename='C:/Users/tmehta/Desktop/Subrajit/Axis Bank/Tableanalysis/AWADHESH KUMAR SINGH-9452230636.xlsx'
		#wb= c.xlsx(r'C:\Users\tmehta\Desktop\Subrajit\Axis Bank\Tabular\Abhishek  Pratap Singh.pdf','Output.xlsx' )

	if excel=="Yes":
		try:
			ed_row= education_cell(sheet,1)			
			ed_col= education_cell(sheet,2)
			#ed_table_rows=education_table_size(ed_row,ed_col,1)		
			ed_table_rows= ed_row+5
			#ed_table_columns=education_table_size(ed_row,ed_col,2)
			ed_table_columns=sheet.ncols
			degree_col= check_colnames(ed_col,ed_table_columns,ed_row,ed_table_rows,1)
			institute_col= check_colnames(ed_col,ed_table_columns,ed_row,ed_table_rows,2)
			board_col= check_colnames(ed_col,ed_table_columns,ed_row,ed_table_rows,3)
			year_col= check_colnames(ed_col,ed_table_columns,ed_row,ed_table_rows,4)
			marks_col= check_colnames(ed_col,ed_table_columns,ed_row,ed_table_rows,5)
			df=create_datatable (ed_col,ed_table_columns,ed_row,ed_table_rows)
			if Is_Post_Graduate:
				None
			else:
				Is_Post_Graduate=df.iloc[0].Post_Graduate
				Post_Graduate_details= df.iloc[0].Post_Graduate_detail
			if df.iloc[0].Post_Graduate_Marks!="":
				PG_percentage= df.iloc[0].Post_Graduate_Marks
			Post_Graduate_College= df.iloc[0].Post_Graduate_School
			
			if Is_Graduate:
				None
			else:
				Is_Graduate=df.iloc[0].Graduate
				Graduate_details= df.iloc[0].Graduate_detail
			if df.iloc[0].Graduate_Marks!="":
				Graduate_percentage= df.iloc[0].Graduate_Marks
			Graduate_College= df.iloc[0].Graduate_School
		except:
			None


	row= [Name_Path,Email_Address,Mobile_Number,YOB,Address_PIN,District,State,Is_Post_Graduate,Is_Graduate,Post_Graduate_details,Graduate_details,Post_Graduate_College,Graduate_College,PG_percentage,Graduate_percentage,PG_Univ_Tier,Graduate_Univ_Tier,Banking_Role,Circle,Region,City,excel,is_ed_table]
	df_master.loc[i]=row	
###cleaning the data
df_master.Post_Graduate_details=[re.sub('[^A-Za-z]+', '', i) for i in df_master.Post_Graduate_details]
df_master.Post_Graduate_details=[i.upper() for i in df_master.Post_Graduate_details]
df_master.Graduate_details=[re.sub('[^A-Za-z]+', '', i) for i in df_master.Graduate_details]
df_master.Graduate_details=[i.upper() for i in df_master.Graduate_details]
df_master.PG_percentage=[re.sub('[^0-9.]+', '', i) for i in df_master.PG_percentage]	
df_master.Graduate_percentage=[re.sub('[^0-9.]+', '', i) for i in df_master.Graduate_percentage]

##cleaning numbers 
df_master["Graduate_percentage"]=df_master["Graduate_percentage"].convert_objects(convert_numeric=True)
df_master["PG_percentage"]=df_master["PG_percentage"].convert_objects(convert_numeric=True)
df_master.loc[df_master["Graduate_percentage"]<1,["Graduate_percentage"]]=df_master.loc[df_master["Graduate_percentage"]<1,["Graduate_percentage"]]*100
df_master.loc[df_master["PG_percentage"]<1,["PG_percentage"]]=df_master.loc[df_master["PG_percentage"]<1,["PG_percentage"]]*100

#calculating new fields like age,marks average etc
df_master["YOB"]=df_master["YOB"].convert_objects(convert_numeric=True)
df_master["Age"]=2016-df_master["YOB"]
df_master["Avg_marks"]= df_master[['Graduate_percentage', 'PG_percentage']].mean(axis=1)
df_master["Category"]=""

for i in range(0,df_master["Name_Path"].count()):
	if df_master["Age"].iloc[i]>24 and df_master["Age"].iloc[i]<26 and df_master["Is_Post_Graduate"].iloc[i]=="Yes" and (df_master["Avg_marks"].iloc[i]>55 or np.isnan(df_master["Avg_marks"].iloc[i])) :
		df_master["Category"].iloc[i]="CSO_AM"
	if df_master["Age"].iloc[i]<26 and df_master["Is_Post_Graduate"].iloc[i]=="No" and (df_master["Avg_marks"].iloc[i]<55 or np.isnan(df_master["Avg_marks"].iloc[i])) :
		df_master["Category"].iloc[i]="BDE"

	


df_master.to_csv('20161230_outputv2.csv')


##cleaning the dataoutput

