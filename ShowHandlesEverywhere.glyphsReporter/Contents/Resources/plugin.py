# encoding: utf-8

###########################################################################################################
#
#
#	Reporter Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Reporter
#
#
###########################################################################################################

from GlyphsApp import OFFCURVE
from GlyphsApp.plugins import *
from AppKit import NSBezierPath, NSPoint, NSSize, NSRect, NSColor

class ShowHandlesEverywhere(ReporterPlugin):
	@objc.python_method
	def settings(self):
		self.menuName = Glyphs.localize({
			'en': u'Handles Everywhere', 
			'de': u'Anfasser überall', 
			'fr': u'les poignées n’importe où'
		})
	@objc.python_method
	def background(self, layer):
		thisFont = layer.parent.parent
		
		# background of layer, or foreground of background layer:
		if Glyphs.defaults["showNodes"]:
			
			# draw handles in background:
			if Glyphs.defaults["showBackground"] and not Glyphs.defaults["showNodesInBackground"] and thisFont.tool != "TextTool":
				if "GSBackgroundLayer" in str(type(layer)):
					background = layer.foreground()
				else:
					background = layer.background
				self.drawHandlesAndNodes( background )
			
			# determine current tool (must not draw with Select All Layers tool):
			# Font.tool cannot differentiate between Select and SelectAllLayers
			try:
				toolClass = Glyphs.currentDocument.windowController().toolEventHandler().className()
			except:
				toolClass = None
		
			# draw handles in visible layers:
			if toolClass != "GlyphsToolSelectAllLayers":
				layerCenter = layer.width/2
				thisGlyph = layer.parent
				for thisLayer in thisGlyph.layers:
					if thisLayer != layer and thisLayer.visible():
						# determine layer color:
						drawColor = thisLayer.colorObject
						if not drawColor:
							drawColor = NSColor.lightGrayColor()
				
						# center layer drawings:
						horizontalMove = layerCenter - thisLayer.width/2
						self.drawHandlesAndNodes( thisLayer, color=drawColor, shift=horizontalMove )
	
	@objc.python_method
	def needsExtraMainOutlineDrawingForInactiveLayer_( self, layer ):
		return True
	
	@objc.python_method		
	def inactiveLayers( self, layer ):
		if not Glyphs.defaults["fillPreview"]:
			scaleDown = 0.7
			self.drawHandlesAndNodes( layer, scaleDown=scaleDown )
	
	@objc.python_method
	def drawHandlesAndNodes( self, thisLayer, scaleDown=0.5, color=NSColor.lightGrayColor(), shift=0.0 ):
		if Glyphs.defaults["showNodes"]:
			handleStroke = scaleDown / self.getScale()
			color.set()
			paths = []
			paths.extend(thisLayer.paths)
			layers = []
			# add paths of components:
			for thisComponent in thisLayer.components:
				transformation = thisComponent.transformStruct()
				componentLayer = thisComponent.componentLayer().copy()
				componentLayer.applyTransform(transformation)
				paths.extend(componentLayer.paths) 
				layers.append(componentLayer)
			for thisPath in paths:
				for thisNode in thisPath.nodes:
					# draw handle sticks:
					if thisNode.type == OFFCURVE:
						if thisNode.prevNode.type != OFFCURVE:
							self.drawLineBetweenNodes( thisNode, thisNode.prevNode, handleStroke, shift=shift )
						else:
							self.drawLineBetweenNodes( thisNode, thisNode.nextNode, handleStroke, shift=shift )
					# draw node circles:
					self.drawCircleForNode( thisNode, factor=scaleDown, shift=shift )
	
	@objc.python_method
	def drawLineBetweenNodes( self, Node1, Node2, handleStrokeWidth, shift=0.0 ):
		p1 = NSPoint( Node1.x+shift, Node1.y )
		p2 = NSPoint( Node2.x+shift, Node2.y )
		lineToBeDrawn = NSBezierPath.alloc().init()
		lineToBeDrawn.setLineWidth_( handleStrokeWidth )
		lineToBeDrawn.moveToPoint_( p1 )
		lineToBeDrawn.lineToPoint_( p2 )
		lineToBeDrawn.stroke()
	
	@objc.python_method		
	def drawCircleForNode(self, node, factor=1.0, shift=0.0 ):
		# calculate handle size:
		handleSizes = (5, 8, 12) # possible user settings
		handleSizeIndex = Glyphs.handleSize # user choice in Glyphs > Preferences > User Preferences > Handle Size
		handleSize = handleSizes[handleSizeIndex]*self.getScale()**-0.9 # scaled diameter
	
		# overall scale factor
		handleSize *= factor
		
		# offcurves are a little smaller:
		if node.type == OFFCURVE:
			handleSize *= 0.8
	
		# selected handles are a little bigger:
		if node.selected:
			handleSize *= 1.45
	
		# draw disc inside a rectangle around point position:
		position = node.position
		rect = NSRect()
		rect.origin = NSPoint(position.x-handleSize/2+shift, position.y-handleSize/2)
		rect.size = NSSize(handleSize, handleSize)
		NSBezierPath.bezierPathWithOvalInRect_(rect).fill()
	

