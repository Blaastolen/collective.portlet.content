import lxml.html
from zope.interface import implements
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.component import getAdapters
from zope.formlib import form
from AccessControl import getSecurityManager

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from plone.app.uuid.utils import uuidToObject
from plone.app.vocabularies.catalog import CatalogSource
from plone.app.blocks.layoutbehavior import ILayoutAware
from plone.memoize import instance

from collective.portlet.content import ContentPortletMessageFactory as _
from zope.i18nmessageid import MessageFactory
__ = MessageFactory("plone")

class IContentPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """


    content = schema.Choice(title=_(u"Content Item"),
        required=True,
        source=CatalogSource(object_provides=ILayoutAware.__identifier__)
    )





class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IContentPortlet)

    portlet_title = u''
    content = None
    item_id = u'main-container'
    template_name = u''

    def __init__(self, content=None):

        self.content = content

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return __(u"Content portlet")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('contentportlet.pt')

    @instance.memoizedproperty
    def content(self):
        """
        Returns the content object or None if it does not exist.
        """
        return uuidToObject(self.data.content)


    def script(self):
        return """$( "#contentportlet" ).load( "%s #content" );""" % self.content.absolute_url()




class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    schema = IContentPortlet
    label = _(u"Add Content Portlet")
    description = _(u"")
    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    label = _(u"Edit Content Portlet")
    description = _(u"")

    schema = IContentPortlet
