#!/usr/bin/env python
# encoding: utf-8

import objc
from Foundation import *
from AppKit import *
import sys, os, re

MainBundle = NSBundle.mainBundle()
path = MainBundle.bundlePath() + "/Contents/Scripts"
if not path in sys.path:
	sys.path.append( path )

import GlyphsApp
Glyphs = NSApplication.sharedApplication()

GlyphsReporterProtocol = objc.protocolNamed( "GlyphsReporter" )

class HandlesEverywhere ( NSObject, GlyphsReporterProtocol ):
	
	def init( self ):
		"""
		Put any initializations you want to make here.
		"""
		try:
			#Bundle = NSBundle.bundleForClass_( NSClassFromString( self.className() ));
			return self
		except Exception as e:
			self.logToConsole( "init: %s" % str(e) )
	
	def interfaceVersion( self ):
		"""
		Distinguishes the API version the plugin was built for. 
		Return 1.
		"""
		try:
			return 1
		except Exception as e:
			self.logToConsole( "interfaceVersion: %s" % str(e) )
	
	def title( self ):
		"""
		This is the name as it appears in the menu in combination with 'Show'.
		E.g. 'return "Nodes"' will make the menu item read "Show Nodes".
		"""
		try:
			return "Handles Everywhere"
		except Exception as e:
			self.logToConsole( "title: %s" % str(e) )
	
	def keyEquivalent( self ):
		"""
		The key for the keyboard shortcut. Set modifier keys in modifierMask() further below.
		Pretty tricky to find a shortcut that is not taken yet, so be careful.
		If you are not sure, use 'return None'. Users can set their own shortcuts in System Prefs.
		"""
		try:
			return None
		except Exception as e:
			self.logToConsole( "keyEquivalent: %s" % str(e) )
	
	def modifierMask( self ):
		"""
		Use any combination of these to determine the modifier keys for your default shortcut:
			return NSShiftKeyMask | NSControlKeyMask | NSCommandKeyMask | NSAlternateKeyMask
		Or:
			return 0
		... if you do not want to set a shortcut.
		"""
		try:
			return 0
		except Exception as e:
			self.logToConsole( "modifierMask: %s" % str(e) )
	
	def drawForegroundForLayer_( self, Layer ):
		"""
		Whatever you draw here will be displayed IN FRONT OF the paths.
		Setting a color:
			NSColor.colorWithCalibratedRed_green_blue_alpha_( 1.0, 1.0, 1.0, 1.0 ).set() # sets RGBA values between 0.0 and 1.0
			NSColor.redColor().set() # predefined colors: blackColor, blueColor, brownColor, clearColor, cyanColor, darkGrayColor, grayColor, greenColor, lightGrayColor, magentaColor, orangeColor, purpleColor, redColor, whiteColor, yellowColor
		Drawing a path:
			myPath = NSBezierPath.alloc().init()  # initialize a path object myPath
			myPath.appendBezierPath_( subpath )   # add subpath to myPath
			myPath.fill()   # fill myPath with the current NSColor
			myPath.stroke() # stroke myPath with the current NSColor
		To get an NSBezierPath from a GSPath, use the bezierPath() method:
			myPath.bezierPath().fill()
		You can apply that to a full layer at once:
			if len( myLayer.paths > 0 ):
				myLayer.bezierPath()       # all closed paths
				myLayer.openBezierPath()   # all open paths
		See:
		https://developer.apple.com/library/mac/documentation/Cocoa/Reference/ApplicationKit/Classes/NSBezierPath_Class/Reference/Reference.html
		https://developer.apple.com/library/mac/documentation/cocoa/reference/applicationkit/classes/NSColor_Class/Reference/Reference.html
		"""
		try:
			pass
		except Exception as e:
			self.logToConsole( "drawForegroundForLayer_: %s" % str(e) )
	
	def drawBackgroundForLayer_( self, Layer ):
		"""
		Whatever you draw here will be displayed BEHIND the paths.
		"""
		try:
			background = Layer.background
			
			if type(background) == GSBackgroundLayer and Glyphs.defaults["showBackground"]:
				scaleDown = 0.5
				NodeSize = self.getHandleSize()
				Scale = self.getScale()
				circleRadius = (NodeSize / Scale) * scaleDown
				handleStroke = scaleDown / Scale
							
				# Off-curve nodes:
				NSColor.lightGrayColor().set()
				handleList = self.listOfHandles( background )
				self.drawLinesBetweenNodePairs( handleList, handleStroke )
				self.drawCirclesAtSize( [p[1] for p in handleList], circleRadius )

				# On-curve nodes:
				self.drawCirclesAtSize( self.listOfNodes( background ), circleRadius )
			
		except Exception as e:
			self.logToConsole( "drawBackgroundForLayer_: %s" % str(e) )
	
	def drawBackgroundForInactiveLayer_( self, Layer ):
		"""
		Whatever you draw here will be displayed behind the paths, but for inactive masters.
		"""
		try:
			if not Glyphs.defaults["fillPreview"]:
				scaleDown = 0.7
				NodeSize = self.getHandleSize()
				Scale = self.getScale()
				circleRadius = (NodeSize / Scale) * scaleDown
				handleStroke = scaleDown / Scale
			
				# Off-curve nodes:
				NSColor.lightGrayColor().set()
				handleList = self.listOfHandles( Layer )
				self.drawLinesBetweenNodePairs( handleList, handleStroke )
				self.drawCirclesAtSize( [p[1] for p in handleList], circleRadius )

				# On-curve nodes:
				#NSColor.darkGrayColor().set()
				self.drawCirclesAtSize( self.listOfNodes( Layer ), circleRadius )
			
		except Exception as e:
			self.logToConsole( "drawBackgroundForInactiveLayer_: %s" % str(e) )
	
	def drawLinesBetweenNodePairs( self, listOfPointPairs, handleStrokeWidth ):
		try:
			linesToBeDrawn   = NSBezierPath.alloc().init()
			
			for thisPointPair in listOfPointPairs:
				fromPoint = thisPointPair[0]
				toPoint   = thisPointPair[1]
				linesToBeDrawn.moveToPoint_( NSPoint(fromPoint.x, fromPoint.y) )
				linesToBeDrawn.lineToPoint_( NSPoint(toPoint.x, toPoint.y) )
				
			linesToBeDrawn.setLineWidth_( handleStrokeWidth )
			linesToBeDrawn.stroke()
		except Exception as e:
			self.logToConsole( "drawLinesBetweenNodePairs: %s" % str(e) )
			
	
	def drawCirclesAtSize( self, listOfPoints, circleRadius ):
		try:
			circlesToBeDrawn = NSBezierPath.alloc().init()
			
			for thisPoint in listOfPoints:
				circlesToBeDrawn.appendBezierPath_( self.markerForPoint( thisPoint, circleRadius ) )
			
			circlesToBeDrawn.fill()
		except Exception as e:
			self.logToConsole( "drawCirclesAtSize: %s" % str(e) )
			
	
	def drawTextAtPoint( self, text, textPosition, fontSize=9.0, fontColor=NSColor.brownColor() ):
		"""
		Use self.drawTextAtPoint( "blabla", myNSPoint ) to display left-aligned text at myNSPoint.
		"""
		try:
			glyphEditView = self.controller.graphicView()
			currentZoom = self.getScale()
			fontAttributes = { 
				NSFontAttributeName: NSFont.labelFontOfSize_( fontSize/currentZoom ),
				NSForegroundColorAttributeName: fontColor }
			displayText = NSAttributedString.alloc().initWithString_attributes_( text, fontAttributes )
			textAlignment = 3 # top left: 6, top center: 7, top right: 8, center left: 3, center center: 4, center right: 5, bottom left: 0, bottom center: 1, bottom right: 2
			glyphEditView.drawText_atPoint_alignment_( displayText, textPosition, textAlignment )
		except Exception as e:
			self.logToConsole( "drawTextAtPoint: %s" % str(e) )
	
	def listOfNodes( self, thisLayer ):
		"""
		Returns a list of all on-curve nodes.
		"""
		try:
			returnList = []
		
			for thisPath in thisLayer.paths:
				for i in range( len( thisPath.nodes )):
					thisNode = thisPath.nodes[ i ]
					if thisNode.type != 65: # not a handle
						returnList.append( thisNode )
							
			return returnList
		except Exception as e:
			self.logToConsole( "getListOfNodesToBeMarked: " + str(e) )
	
	def listOfHandles( self, thisLayer ):
		"""
		Returns a list of all on-curve nodes.
		"""
		try:
			returnList = []
		
			for thisPath in thisLayer.paths:
				for i in range( len( thisPath.nodes )):
					thisNode = thisPath.nodes[ i ]
					prevNode = thisPath.nodes[ i-1 ]
					nextNode = thisPath.nodes[ i+1 ]
				
					if thisNode.type == 65:
						# a selected off-curve
						if prevNode.type != 65:
							returnList.append( (prevNode, thisNode) )
						elif nextNode.type != 65:
							returnList.append( (nextNode, thisNode) )

			return returnList
		except Exception as e:
			self.logToConsole( "getListOfHandlesToBeMarked_ " + str(e) )
	
	def markerForPoint( self, thisPoint, markerWidth ):
		"""
		Returns a circle with thisRadius around thisPoint.
		"""
		try:
			myRect = NSRect( ( thisPoint.x - markerWidth * 0.5, thisPoint.y - markerWidth * 0.5 ), ( markerWidth, markerWidth ) )
			return NSBezierPath.bezierPathWithOvalInRect_( myRect )
		except Exception as e:
			self.logToConsole( "markerForPoint_ " + str(e) )
	
	def needsExtraMainOutlineDrawingForInactiveLayer_( self, Layer ):
		"""
		Return False to disable the black outline. Otherwise remove the method.
		"""
		return False
	
	def getHandleSize( self ):
		"""
		Returns the current handle size as set in user preferences.
		Use: self.getHandleSize() / self.getScale()
		to determine the right size for drawing on the canvas.
		"""
		try:
			Selected = NSUserDefaults.standardUserDefaults().integerForKey_( "GSHandleSize" )
			if Selected == 0:
				return 5.0
			elif Selected == 2:
				return 10.0
			else:
				return 7.0 # Regular
		except Exception as e:
			self.logToConsole( "getHandleSize: HandleSize defaulting to 7.0. %s" % str(e) )
			return 7.0

	def getScale( self ):
		"""
		self.getScale() returns the current scale factor of the Edit View UI.
		Divide any scalable size by this value in order to keep the same apparent pixel size.
		"""
		try:
			return self.controller.graphicView().scale()
		except:
			self.logToConsole( "Scale defaulting to 1.0" )
			return 1.0
	
	def setController_( self, Controller ):
		"""
		Use self.controller as object for the current view controller.
		"""
		try:
			self.controller = Controller
		except Exception as e:
			self.logToConsole( "Could not set controller" )
	
	def logToConsole( self, message ):
		"""
		The variable 'message' will be passed to Console.app.
		Use self.logToConsole( "bla bla" ) for debugging.
		"""
		myLog = "Show %s plugin:\n%s" % ( self.title(), message )
		print myLog
		NSLog( myLog )