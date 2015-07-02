import sublime, sublime_plugin
from collections import OrderedDict
from os.path import basename

class drdBkmarksClass( OrderedDict ):

	@staticmethod
	def name( b ):
		return 'drdB.{}'.format( b )
	
	def setB( self, b, view ):
		name = drdBkmarksClass.name( b )
		if name in self:
			view_id = self[ name ][ 0 ]
			for w in sublime.windows():
				views = filter( lambda v: v.id() == view_id,  w.views() )
				for v in views:
					v.erase_regions( name )
					break
		mark = view.sel()[ 0 ]
		
		self[ name ] = ( view.id(), b, view.substr( view.line( mark ) ), basename( view.file_name() ) )
		return ( name, mark )
	
	def getB( self, b ):
		name = drdBkmarksClass.name( b )
		return ( name, self.get( name, None ) )
		
drdBookmarks = drdBkmarksClass()

class DrdBookmarkSet( sublime_plugin.TextCommand ):
	def run(self, edit, **args ):
		b = args.get( 'character', '.' )
		( name, mark ) = drdBookmarks.setB( b, self.view )
		self.view.add_regions( name, [ mark ], 'mark', 'bookmark', sublime.HIDDEN )
		
class DrdBookmarkGoto( sublime_plugin.TextCommand ):
	def run( self, edit, **args ):
		b = args.get( 'character', '.' )
		( name, ( view_id, b, line, file_name ) ) = drdBookmarks.getB( b )
		if view_id == None:
			sublime.status_message( 'Bookmark `{}` not found!'.format( b ) )
		else:
			for w in sublime.windows():
				for v in w.views():
					if v.id() == view_id:
						region = v.get_regions( name )
						if region:
							v.sel().clear()
							v.sel().add( region[ 0 ] )
							v.show( region[ 0 ] )
							w.focus_view( v )
							return
			else:
				sublime.status_message( 'Bookmark `{}` not found!'.format( b ) )

class DrdBookmarkClearAll( sublime_plugin.TextCommand ):
	def run( self, edit, **args ):
		if( len( drdBookmarks ) > 0 ):
			sublime.status_message( 'Clear all bookmarks' )
			if( sublime.ok_cancel_dialog( 'Do you really want to clear all bookmarks?' ) ):
				for ( name, ( view_id, b, line, file_name ) ) in drdBookmarks.items():
					for w in sublime.windows():
						for v in w.views():
							if v.id() == view_id:
								v.erase_regions( name )	
				drdBookmarks.clear()
				sublime.status_message( 'All bookmarks cleared!' )
		else:
			sublime.status_message( 'No bookmarks!' );
		return

class DrdBookmarkListCommand(sublime_plugin.TextCommand):
	def __goto__( self, idx ):
		if( idx >= 0 ):
			k = list( drdBookmarks.keys() )[ idx ]
			self.view.run_command( 'drd_bookmark_goto', { 'character': k.split( '.' )[ -1 ] } )
		return
	def run(self, edit, **args ) :
		if( len( drdBookmarks ) > 0 ):
			bkms = list()
			for ( name, ( view_id, b, line, file_name ) ) in drdBookmarks.items():
				print( name, view_id, b ,line )
				bkms.append( [ b, file_name, line ] )
			try:
				sublime.status_message( 'Pick a bookmark ...' )
				sublime.active_window().show_quick_panel( bkms, lambda idx: self.__goto__( idx ) )
			except Exception as e :
				print( 'ERR: DrdBookmarksListCommand: {}'.format( e ) )
		else:
			sublime.status_message( 'No bookmarks!' )
		return
