import arcpy
import math


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
			displayName="V (m/sec)",
			name="skor",
			datatype="GPDouble",
			parameterType="Required",
			direction="Input")
			
		param0.value=5
		
		param1 = arcpy.Parameter(
			displayName="D (m)",
			name="diam",
			datatype="GPDouble",
			parameterType="Required",
			direction="Input")
			
		param1.value=0.7
			
		param2 = arcpy.Parameter(
			displayName="v (m^2/s)",
			name="vyazk",
			datatype="GPDouble",
			parameterType="Required",
			direction="Input")
			
		param2.value=0.0001
			
		param3 = arcpy.Parameter(
			displayName="Pin (atm)",
			name="davlIn",
			datatype="GPDouble",
			parameterType="Required",
			direction="Input")
			
		param3.value=50
			
		param4 = arcpy.Parameter(
			displayName="Pout (atm)",
			name="davlOut",
			datatype="GPDouble",
			parameterType="Required",
			direction="Input")
			
		param4.value=1
			
		param5 = arcpy.Parameter(
			displayName="d (m)",
			name="razr",
			datatype="GPDouble",
			parameterType="Required",
			direction="Input")
			
		param5.value=0.02
			
		param6 = arcpy.Parameter(
			displayName="t (hours)",
			name="time",
			datatype="GPDouble",
			parameterType="Required",
			direction="Input")
			
		param6.value=2.5
			
		return [param0, param1, param2, param3, param4, param5, param6]

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
		V = parameters[0].value
		D = parameters[1].value
		v = parameters[2].value
		Pin = parameters[3].value * 100000
		Pout = parameters[4].value * 100000
		d = parameters[5].value
		t = parameters[6].value
		
		Re = V * D / v
		
		if Re < 300:
			M = Re / (1.5 + 1.4 * Re)
		elif Re < 10000:
			M = 0.592 + 0.27 / pow(Re, (1/6))
		else:
			M = 0.592 + 5.5 / math.sqrt(Re)
			
		H = (Pin - Pout) / (900 * 10)
		
		f = 3.14 * pow(d, 2) / 4
		
		T = t * 60 * 60
		
		V = M * f * H * T
		
		test = arcpy.GetParameterAsText(0);
		
		arcpy.AddMessage(test);
		
		arcpy.AddMessage("Еhe volume of spilled oil is equal, cubic meters:")
		arcpy.AddMessage(V)
		
		return
