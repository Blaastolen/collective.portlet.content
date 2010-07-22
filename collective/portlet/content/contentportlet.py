from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

try:
    from Products.LinguaPlone.interfaces import ITranslatable
    LINGUAPLONE_SUPPORT = True
except ImportError:
    # Linguaplone not installed
    LINGUAPLONE_SUPPORT = False

from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

from collective.portlet.content import ContentPortletMessageFactory as _


class IContentPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    content = schema.Choice(title=_(u"Target content object"),
                            description=_(u"Find the items to show"),
                            required=True,
                            source=SearchableTextSourceBinder({}, default_query='path:'))


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IContentPortlet)

    content = u""

    def __init__(self, content=None):
        self.content = content

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Content portlet"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('content.pt')

    def text(self):
        if not self.data.content:
            return ''
        portalpath = getToolByName(self.context, 'portal_url').getPortalPath()
        ob = self.context.unrestrictedTraverse(str(portalpath + self.data.content))
        if LINGUAPLONE_SUPPORT:
            tool = getToolByName(self.context, 'portal_languages', None)
            if tool is not None and ITranslatable.providedBy(ob):
                lang = tool.getLanguageBindings()[0]
                ob = ob.getTranslation(lang) or ob
                return ob.getText().decode(ob.getCharset())

        return ob.getText()


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IContentPortlet)
    form_fields['content'].custom_widget = UberSelectionWidget

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IContentPortlet)
    form_fields['content'].custom_widget = UberSelectionWidget
