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
import json as js
from django.db.models import Sum
from DataViz.models import Contrat, Approbateur

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
				approbName = row['APPROBATEUR'].replace("É", "E").replace("Ç", "C").replace("È", "E").lower()
				NbrApprob = Approbateur.objects.filter(approbateur = approbName).count()
				if NbrApprob < 1 :
					a = Approbateur()
					a.LoadFromCSVLine(row)
					a.save()

	return HttpResponse(template.render(context, request))

def tree(request, workstation="undefined"):
	print()
	template = loader.get_template('tree.html')
	


	#Generate context for the tree	
	context = {'graph':"/dataviz/json",
				
			}

	return HttpResponse(template.render(context, request))

def json(r):
	print()
	listNode = {}
	listContratDict = {}
	G=nx.DiGraph()
	#nx.set_node_attributes(G, "value", "nope")
	#G.add_node(1)
	
	#print(Listcontrat)


	# G.add_node(Orphan.pid, name=Orphan.contratname)
	G.add_node(-1, name="Root")

	## Add the Approbateur as level one leaf
	ListApprob = Approbateur.objects.all()
	for approb in ListApprob:
		G.add_node(approb.approb_id, name=approb.approbateur)
		G.add_edge(-1,approb.approb_id)
		print("Test")

	# Attach to contract to the approbateur
	ListContracts = Contrat.objects.all()
	for contrat in ListContracts:
		try:
			currentApprob = Approbateur.objects.filter(approbateur=contrat.approbateur)[0]
			#G.add_node(contrat.contrat_id, value=contrat.montant)
			#G.add_edge(currentApprob.approb_id,contrat.contrat_id)
			
		except KeyError:
			print("Err")
			#G.add_node(contrat.contrat_id, name=contrat.montant)
			#G.add_edge(-1,contrat.contrat_id)

	# G.add_node(contrat.contrat_id, value=contrat.montant)
	# G.add_edge(-1,contrat.contrat_id)
	print(nx.edges(G))
	print("lolilol")

	data = json_graph.tree_data(G, root=-1)
	context = js.dumps(data)
	print(context)


	#context = {}
	return HttpResponse(context)

def force_layout_json(request):

	# Prepare first nodes

	# Array to store nodes:
	arrayNodeLayout = []
	arrayForceLayout = []
	sumPerApprob = {}
	colorScale = {}
	lastColor = 2



	ListContracts = Contrat.objects.all()
	# Let's create a color scale

	for contrat in ListContracts:
		try:
			if(colorScale[contrat.service]):
				pass
		except:
			colorScale[contrat.service] = lastColor
			lastColor += 1

		if(contrat.approbateur == "INTERFACE"):
			print("encule")
			print(contrat)
		if(contrat.approbateur == "Interface"):
			print("non-encule")
			print(contrat)
		arrayNodeLayout.insert(0, {"id" : contrat.contrat_id, "group" : colorScale[contrat.service]})
		arrayForceLayout.insert(0, {"source" : contrat.approbateur, "target" : contrat.contrat_id , "value": contrat.montant*0.001})

	ListApprob = Approbateur.objects.all()

	arrayNodeLayout.append({"id" : "ROOT", "group" : 0})
	for approb in ListApprob:
		print(approb.approbateur)

		iTotalContrats = Contrat.objects.all().filter(approbateur=approb.approbateur).aggregate(Sum('montant'))

		if(iTotalContrats["montant__sum"]):
			arrayNodeLayout.append({"id" : approb.approbateur, "group" : 1})
			arrayForceLayout.append({"source" : "ROOT", "target" : approb.approbateur , "value": (iTotalContrats["montant__sum"]*0.001)/3})


	DictResult = {}
	DictResult["nodes"] = arrayNodeLayout
	DictResult["links"] = arrayForceLayout
	context = js.dumps(DictResult)

	return HttpResponse(context)



def force_layout(request):
	print()
	template = loader.get_template('force_layout.html')
	


	#Generate context for the tree	
	context = {'graph':"/dataviz/force_layout_json",				
			}

	return HttpResponse(template.render(context, request))


