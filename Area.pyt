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
		
		startX = 117
		startY = 56
		points = []
		
		for x in range(10):
			points.append([])
			for y in range(10):
				result = arcpy.GetCellValue_management("C:/arc/srtm_60_01/srtm_60_01.tif", str(startX+float(x)/10) + " " + str(startY+float(x)/10))
				height = int(result.getOutput(0))
				point = {
					"coord" : {"x" : (startX+float(x)/10), "y" : startY+float(x)/10},
					"height" : height
					}
				points[x].append(point)
				(points)
		
		arcpy.AddMessage(points)
		
		return
