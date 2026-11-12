from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR, LOG_NOTE
from frameworks.wulf import ViewModel
from gui.impl.pub.view_component import ViewComponent
from openwg_gameface import gf_mod_inject

from gui.mods.maksforge_garage_filter_extras import popup

MODEL_NAME = 'maksforge_garage_filter_extras.FilterToggleView'
ASSETS = 'coui://gui/gameface/mods/maksforge_garage_filter_extras/FilterToggleView/FilterToggleView'
TOOLTIP_HEADER = 'Non-premium only'
TOOLTIP_BODY = "Shows only tanks that are not premium. The opposite of the game's Premium filter, so don't turn both on."


class FilterToggleModel(ViewModel):
    __slots__ = ('onToggleNonPremium', 'onShowTooltip', 'onHideTooltip', 'onJsLog')

    def __init__(self, properties=3, commands=4):
        super(FilterToggleModel, self).__init__(properties=properties, commands=commands)

    def getVisible(self):
        return self._getBool(0)

    def setVisible(self, value):
        self._setBool(0, value)

    def getOnlyNonPremium(self):
        return self._getBool(1)

    def setOnlyNonPremium(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(FilterToggleModel, self)._initialize()
        self._addBoolProperty('visible', False)
        self._addBoolProperty('onlyNonPremium', False)
        self.onToggleNonPremium = self._addCommand('onToggleNonPremium')
        self.onShowTooltip = self._addCommand('onShowTooltip')
        self.onHideTooltip = self._addCommand('onHideTooltip')
        self.onJsLog = self._addCommand('onJsLog')
        gf_mod_inject(self, MODEL_NAME, styles=[ASSETS + '.css'], modules=[ASSETS + '.js'])


class FilterToggleView(ViewComponent):

    def __init__(self, layoutID):
        super(FilterToggleView, self).__init__(layoutID=layoutID, model=FilterToggleModel)

    @property
    def viewModel(self):
        return super(FilterToggleView, self).getViewModel()

    def show(self, settings):
        with self.viewModel.transaction() as model:
            model.setVisible(bool(settings.get('enabled')))
            model.setOnlyNonPremium(bool(settings.get('onlyNonPremium')))

    def _onLoading(self, *args, **kwargs):
        super(FilterToggleView, self)._onLoading(*args, **kwargs)
        popup.attach(self)

    def _finalize(self):
        popup.detach(self)
        super(FilterToggleView, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.onToggleNonPremium, self.__onToggleNonPremium),
                (self.viewModel.onShowTooltip, self.__onShowTooltip),
                (self.viewModel.onHideTooltip, self.__onHideTooltip),
                (self.viewModel.onJsLog, self.__onJsLog))

    def __onToggleNonPremium(self, *args):
        try:
            popup.toggle_non_premium()
        except Exception:
            LOG_CURRENT_EXCEPTION()

    def __onShowTooltip(self, *args):
        try:
            from gui.shared.utils.functions import makeTooltip
            _tooltipManager().onCreateComplexTooltip(makeTooltip(header=TOOLTIP_HEADER, body=TOOLTIP_BODY), 'INFO')
        except Exception:
            LOG_CURRENT_EXCEPTION()

    def __onHideTooltip(self, *args):
        try:
            _tooltipManager().hide()
        except Exception:
            LOG_CURRENT_EXCEPTION()

    def __onJsLog(self, args=None):
        args = args or {}
        message = '%s [JS] %s' % (popup.LOG_PREFIX, args.get('msg', ''))
        if args.get('level') == 'error':
            LOG_ERROR(message)
        else:
            LOG_NOTE(message)


def _tooltipManager():
    from helpers import dependency
    from skeletons.gui.app_loader import IAppLoader
    return dependency.instance(IAppLoader).getApp().getToolTipMgr()
