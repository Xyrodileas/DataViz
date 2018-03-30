from django.http import JsonResponse
from django.http import HttpResponse
from django.template import loader, Context
from django.shortcuts import render
from networkx.readwrite import json_graph
import csv
from django.db import connection
from django import forms
import networkx as nx
from io import StringIO

from App.models import Contrat, Approbateur
# Create your views here.
# BEGIN ANSIBLE MANAGED BLOCK
def index(request):
  template = loader.get_template('home.html')
  
  context = {}
  return HttpResponse(template.render(context, request))
# END ANSIBLE MANAGED BLOCK

def upload_data(request):
	template = loader.get_template('upload.html')
	
	class UploadContractForm(forms.Form):
		Contrats = forms.FileField(label='Contrats')



	#Generate context for the tree	
	context = {'Contrats':UploadContractForm(),
				
			}

	return HttpResponse(template.render(context, request))

def upload_success(request):
	template = loader.get_template('upload_done.html')
	uploadType = "none"
	#Generate context
	context = {	}
	WorkstationDict = {}

	if request.method == 'POST':
		
		csvfile = 0

		#try:
		print("Get result csv")
		#csvfile =  StringIO(request.FILES['HuntSocket'].read())
		csvfile = StringIO(request.FILES['Contrats'].read().decode('utf-8'))
		uploadType = "Contrats"
		# except :
		# 	try :
		# 		csvfile = StringIO(request.FILES['LOL'].read().decode('utf-8'))
		# 		uploadType = "LOL"
		# 	except :
		# 		try :
		# 			csvfile = StringIO(request.FILES['INCEPTION'].read().decode('utf-8'))
		# 			uploadType = "INCEPTION"
		# 		except :
		# 			print("INCEPTION")

		
		dicfile = csv.DictReader(csvfile)

		HuntID = ""
		for row in dicfile:

			if uploadType == "Contrats" :
				#Check if numero contract exist
				NbrContrat = Contrat.objects.filter(numero = row['NUMÉRO']).count()
				if NbrContrat < 1 :
					s = Contrat()
					s.LoadFromCSVLine(row)
					s.save()
				# Check if approbateur exist
				NbrApprob = Approbateur.objects.filter(approbateur = row['APPROBATEUR']).count()
				if NbrApprob < 1 :
					a = Approbateur()
					a.LoadFromCSVLine(row)
					a.save()

	return HttpResponse(template.render(context, request))

def tree(request, workstation="undefined"):
	print()
	template = loader.get_template('tree.html')
	


	#Generate context for the tree	
	context = {'graph':"/front/json/"+workstation,
				
			}

	return HttpResponse(template.render(context, request))

def json(r):
	print()
	listNode = {}
	listContratDict = {}
	G=nx.DiGraph()
	nx.set_node_attributes(G, 'key', "value")
	#G.add_node(1)
	
	#print(Listcontrat)


	# G.add_node(Orphan.pid, name=Orphan.contratname)
	G.add_node(-1, name="Root")

	## Add the Approbateur as level one leaf
	ListApprob = Approbateur.objects.all()
	for approb in ListApprob:
		G.add_node(approb.approb_id, value=approb.approbateur)
		G.add_edge(-1,approb.approb_id)

	# Attach to contract to the approbateur
	ListContracts = Contrat.objects.all()
	for contrat in ListContracts:
		try:
			currentApprob = Approbateur.objects.filter(approbateur=contrat.approbateur)[0]
			G.add_node(contrat.contrat_id, value=contrat.montant)
			G.add_edge(currentApprob.approb_id,contrat.contrat_id)
			
		except KeyError:
			print("Err")



	print("lolilol")
	context = json_graph.tree_data(G, -1)


	context = {}
	return JsonResponse(context)