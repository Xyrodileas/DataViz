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
from django.db.models import Sum, Count, Q
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

def treemap_json(request):

	# Prepare first nodes

	# Array to store nodes:
	arrayApprobateurs = []
	arrayRoot = []

	ListApprob = Approbateur.objects.all()

	
	for approb in ListApprob:
		#print(approb.approbateur)
		children = []

		ListContracts = Contrat.objects.all().filter(approbateur=approb.approbateur)
		for contract in ListContracts:
			children.append({ "name" : contract.description, "size" : contract.montant })

		arrayApprobateurs.append({ "name" : approb.approbateur, "children" : children })
			

	rootLeaf = {"name" : "Montréal", "children" : arrayApprobateurs}

	
	context = js.dumps(rootLeaf)

	return HttpResponse(context)

def treemap(request):
	print()
	template = loader.get_template('treemap.html')
	


	#Generate context for the tree	
	context = {'graph':"/dataviz/treemap_json",				
			}

	return HttpResponse(template.render(context, request))

def concentric_json(request, skip=0):

	# CONST
	maxServices = 15
	currentService = skip
	print(skip)
	# Array to store nodes:
	arrayRoot = []

	ListServices = Contrat.objects.values('service').annotate(serviceNumber=Count('contrat_id')).annotate(montantTot=Sum('montant')).annotate(year2017=Count('date', filter=Q(date__year=2015))).annotate(moreThan10K=Count('contrat_id', filter=Q(montant__gte=1000)))

	
	for service in ListServices:
		#print(currentService)
		arrayRoot.append({ "service" : service["service"], "nbrContrat" : service["serviceNumber"], "montantTot" : service["montantTot"], "moreThan10K": service["moreThan10K"], "year2017" : service["year2017"] })
	
	
	context = js.dumps(arrayRoot)

	return HttpResponse(context)

def concentric(request, skip=0):
	print()
	template = loader.get_template('concentric.html')
	


	#Generate context for the tree	
	if(skip == 0):
		context = {'graph':"/dataviz/concentric_json",				
				}
	else:
		context = {'graph':"/dataviz/concentric_json/" + skip + "/",				
		}

	return HttpResponse(template.render(context, request))

def circular_tree_json(request, skip=0):

	# CONST
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
	writer = csv.writer(response)
	writer.writerow(['id', 'value'])
	# Array to store nodes:
	arrayRoot = []
	dictApprob = {}
	csv_data = ()
	ListContract = Contrat.objects.all()

	#arrayRoot.append("root,")
	#csv_data = csv_data + ("root,",'')
	writer.writerow(['MTL', ''	])

	for contract in ListContract:
		try:
			if(contract.approbateur == "" or contract.approbateur == " "):
				pass
			if(dictApprob[contract.approbateur]):
				pass
		except:
			#arrayRoot.append("root." + contract.approbateur + ",")
			#csv_data = csv_data + ("root." + contract.approbateur + "." + contract.description, '')
			dictApprob[contract.approbateur] = 1
			if (not contract.approbateur.replace(",","").replace(" ","").replace(".","") == ""):
				writer.writerow(["MTL." + contract.approbateur.replace(",","").replace(" ","").replace(".",""), ""])
		#print(currentService)
		#arrayRoot.append("root." + contract.approbateur + "." + contract.description + "," + str(contract.montant))
		#csv_data = csv_data +("root." + contract.approbateur + "." + contract.description, str(contract.montant))
		if (not contract.approbateur.replace(",","").replace(" ","") == ""):
			writer.writerow(["MTL." + contract.approbateur.replace(",","").replace(" ","").replace(".","") + "." + contract.description, contract.montant])
	

	print("wtf")

	return response

def circular_tree(request, skip=0):
	print()
	template = loader.get_template('circular_tree.html')
	


	#Generate context for the tree	

	context = {'graph':"/dataviz/circular_tree_json",				
			}


	return HttpResponse(template.render(context, request))

def histogram_json(request, skip=0):

	# Prepare first nodes

	# Array to store nodes:
	arrayApprobateurs = []
	arrayRoot = []

	ListApprob = Approbateur.objects.all()

	
	for approb in ListApprob:
		#print(approb.approbateur)
		children = []

		nbrContracts = Contrat.objects.all().filter(approbateur=approb.approbateur).count()

		arrayApprobateurs.append({ "Letter" : approb.approbateur, "Freq" : nbrContracts })
			


	
	context = js.dumps(arrayApprobateurs)

	return HttpResponse(context)

def histogram(request, skip=0):
	print()
	template = loader.get_template('histogram.html')
	


	#Generate context for the tree	

	context = {'graph':"/dataviz/histogram_json",				
			}


	return HttpResponse(template.render(context, request))