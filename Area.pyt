import arcpy
import math
import time


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [Tool]


class Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Tool"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
    #Define parameter definitions
    # First parameter
		param0 = arcpy.Parameter(
			displayName="V",
			name="vol",
			datatype="GPDouble",
			parameterType="Required",
			direction="Input")
			
		param0.value=5
			
		param1 = arcpy.Parameter(
			displayName="h",
			name="h",
			datatype="GPDouble",
			parameterType="Required",
			direction="Input")
			
		param1.value=5
		
		param2 = arcpy.Parameter(
			displayName="delta R",
			name="Radius increment",
			datatype="GPDouble",
			parameterType="Required",
			direction="Input")
			
		param2.value=5
			
		return [param0, param1, param2]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
		
		vol = parameters[0].value
		h = parameters[1].value
		deltaR = parameters[2].value
		
		sMax = vol/h
		"""Current radius"""
		r = 0
		"""Current surface area"""
		s = 0
		
		'''arcpy.env.workspace = "C:\arc\My\DB.gdb"'''
		arcpy.Buffer_analysis("StartPoint", "C:\arc\My\DB.gdb\Buffer6", "15 Meters")
		
		# get the map document
		mxd = arcpy.mapping.MapDocument("CURRENT")

		# get the data frame
		#df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

		# create a new layer
		#newlayer = arcpy.mapping.Layer("C:\Users\i am kerel\Documents\ArcGIS\Default.gdb\StartPoint_Buffer10")

		# add the layer to the map at the bottom of the TOC in data frame 0
		#arcpy.mapping.AddLayer(df, newlayer,"BOTTOM")
		
		while s < sMax:
			r += deltaR
			s = 3.14 * pow(r, 2)
			arcpy.AddMessage("Surface area:")
			arcpy.AddMessage(s)
			
		
		return