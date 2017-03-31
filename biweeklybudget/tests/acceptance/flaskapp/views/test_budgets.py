"""
The latest version of this package is available at:
<http://github.com/jantman/biweeklybudget>

################################################################################
Copyright 2016 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

    This file is part of biweeklybudget, also known as biweeklybudget.

    biweeklybudget is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    biweeklybudget is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with biweeklybudget.  If not, see <http://www.gnu.org/licenses/>.

The Copyright and Authors attributions contained herein may not be removed or
otherwise altered, except to add the Author attribution of a contributor to
this work. (Additional Terms pursuant to Section 7b of the AGPL v3)
################################################################################
While not legally required, I sincerely request that anyone who finds
bugs please submit them at <https://github.com/jantman/biweeklybudget> or
to me via email, and that you send any contributions or improvements
either as a pull request on GitHub, or to me via email.
################################################################################

AUTHORS:
Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
################################################################################
"""

import pytest

from biweeklybudget.tests.acceptance_helpers import AcceptanceHelper
from biweeklybudget.models.budget_model import Budget


@pytest.mark.acceptance
@pytest.mark.usefixtures('class_refresh_db', 'refreshdb', 'testflask')
class TestBudgets(AcceptanceHelper):

    @pytest.fixture(autouse=True)
    def get_page(self, base_url, selenium):  # noqa
        self.baseurl = base_url
        selenium.get(base_url + '/budgets')

    def test_heading(self, selenium):
        heading = selenium.find_element_by_class_name('navbar-brand')
        assert heading.text == 'Budgets - BiweeklyBudget'

    def test_nav_menu(self, selenium):
        ul = selenium.find_element_by_id('side-menu')
        assert ul is not None
        assert 'nav' in ul.get_attribute('class')
        assert ul.tag_name == 'ul'

    def test_notifications(self, selenium):
        div = selenium.find_element_by_id('notifications-row')
        assert div is not None
        assert div.get_attribute('class') == 'row'

    def test_initial_data(self, selenium):
        ptable = selenium.find_element_by_id('table-periodic-budgets')
        ptexts = self.tbody2textlist(ptable)
        stable = selenium.find_element_by_id('table-standing-budgets')
        stexts = self.tbody2textlist(stable)
        assert ptexts == [
            ['Periodic1 (1)', '$100.00'],
            ['Periodic2 (2)', '$234.00']
        ]
        assert stexts == [
            ['Standing1 (4)', '$1,284.23'],
            ['Standing2 (5)', '$9,482.29']
        ]
        pelems = self.tbody2elemlist(ptable)
        selems = self.tbody2elemlist(stable)
        assert pelems[1][0].get_attribute(
            'innerHTML') == '<a href="javascript:budgetModal(2)">' \
                            'Periodic2 (2)</a>'
        assert selems[0][0].get_attribute(
            'innerHTML') == '<a href="javascript:budgetModal(4)">' \
                            'Standing1 (4)</a>'


@pytest.mark.acceptance
@pytest.mark.usefixtures('class_refresh_db', 'refreshdb', 'testflask')
class TestEditPeriodic1(AcceptanceHelper):

    def test_0_verify_db(self, testdb):
        b = testdb.query(Budget).get(1)
        assert b.name == 'Periodic1'
        assert b.is_periodic is True
        assert b.description == 'P1desc'
        assert b.starting_balance == 100.00
        assert b.is_active is True

    def test_1_populate_modal(self, base_url, selenium):
        selenium.get(base_url + '/budgets')
        link = selenium.find_element_by_xpath('//a[text()="Periodic1 (1)"]')
        link.click()
        modal, title, body = self.get_modal_parts(selenium)
        self.assert_modal_displayed(modal, title, body)
        assert title.text == 'Edit Budget 1'
        assert selenium.find_element_by_id('budget_frm_name').get_attribute(
            'value') == 'Periodic1'
        assert selenium.find_element_by_id(
            'budget_frm_type_periodic').is_selected()
        assert selenium.find_element_by_id(
            'budget_frm_type_standing').is_selected() is False
        assert selenium.find_element_by_id(
            'budget_frm_description').get_attribute('value') == 'P1desc'
        assert selenium.find_element_by_id(
            'budget_frm_starting_balance').get_attribute('value') == '100'
        assert selenium.find_element_by_id(
            'budget_frm_group_starting_balance').is_displayed()
        assert selenium.find_element_by_id(
            'budget_frm_current_balance').get_attribute('value') == ''
        assert selenium.find_element_by_id(
            'budget_frm_group_current_balance').is_displayed() is False
        assert selenium.find_element_by_id('budget_frm_active').is_selected()

    def test_2_update_modal(self, base_url, selenium):
        # Fill in the form
        selenium.get(base_url + '/budgets')
        link = selenium.find_element_by_xpath('//a[text()="Periodic1 (1)"]')
        link.click()
        modal, title, body = self.get_modal_parts(selenium)
        self.assert_modal_displayed(modal, title, body)
        name = selenium.find_element_by_id('budget_frm_name')
        name.clear()
        name.send_keys('EditedPeriodic1')
        desc = selenium.find_element_by_id('budget_frm_description')
        desc.clear()
        desc.send_keys('EditedP1desc')
        sb = selenium.find_element_by_id('budget_frm_starting_balance')
        sb.clear()
        sb.send_keys('2345.67')
        selenium.find_element_by_id('budget_frm_active').click()
        assert selenium.find_element_by_id(
            'budget_frm_active').is_selected() is False
        # submit the form
        selenium.find_element_by_id('modalSaveButton').click()
        self.wait_for_jquery_done(selenium)
        # check that we got positive confirmation
        _, _, body = self.get_modal_parts(selenium)
        x = body.find_elements_by_tag_name('div')[0]
        assert 'alert-success' in x.get_attribute('class')
        assert x.text.strip() == 'Successfully saved Budget 1 in database.'
        # dismiss the modal
        selenium.find_element_by_id('modalCloseButton').click()

    def test_3_verify_db(self, testdb):
        b = testdb.query(Budget).get(1)
        print("3_verify: %s" % vars(b))
        assert b.name == 'EditedPeriodic1'
        assert b.is_periodic is True
        assert b.description == 'EditedP1desc'
        assert float(b.starting_balance) == 2345.6700
        assert b.is_active is False

    def test_4_verify_page(self, selenium):
        # test that updated budget was removed from the page
        assert 'Periodic1' not in selenium.page_source


@pytest.mark.acceptance
@pytest.mark.usefixtures('class_refresh_db', 'refreshdb', 'testflask')
class TestEditPeriodic2(AcceptanceHelper):

    def test_1_populate_modal(self, base_url, selenium):
        selenium.get(base_url + '/budgets')
        link = selenium.find_element_by_xpath('//a[text()="Periodic2 (2)"]')
        link.click()
        modal, title, body = self.get_modal_parts(selenium)
        self.assert_modal_displayed(modal, title, body)
        assert title.text == 'Edit Budget 2'
        assert selenium.find_element_by_id('budget_frm_name').get_attribute(
            'value') == 'Periodic2'
        assert selenium.find_element_by_id(
            'budget_frm_type_periodic').is_selected()
        assert selenium.find_element_by_id(
            'budget_frm_type_standing').is_selected() is False
        assert selenium.find_element_by_id(
            'budget_frm_description').get_attribute('value') == 'P2desc'
        assert selenium.find_element_by_id(
            'budget_frm_starting_balance').get_attribute('value') == '234'
        assert selenium.find_element_by_id(
            'budget_frm_group_starting_balance').is_displayed()
        assert selenium.find_element_by_id(
            'budget_frm_current_balance').get_attribute('value') == ''
        assert selenium.find_element_by_id(
            'budget_frm_group_current_balance').is_displayed() is False
        assert selenium.find_element_by_id('budget_frm_active').is_selected()


@pytest.mark.acceptance
@pytest.mark.usefixtures('class_refresh_db', 'refreshdb', 'testflask')
class TestEditStanding1(AcceptanceHelper):

    def test_1_populate_modal(self, base_url, selenium):
        selenium.get(base_url + '/budgets')
        link = selenium.find_element_by_xpath('//a[text()="Standing1 (4)"]')
        link.click()
        modal, title, body = self.get_modal_parts(selenium)
        self.assert_modal_displayed(modal, title, body)
        assert title.text == 'Edit Budget 4'
        assert selenium.find_element_by_id('budget_frm_name').get_attribute(
            'value') == 'Standing1'
        assert selenium.find_element_by_id(
            'budget_frm_type_periodic').is_selected() is False
        assert selenium.find_element_by_id(
            'budget_frm_type_standing').is_selected()
        assert selenium.find_element_by_id(
            'budget_frm_description').get_attribute('value') == 'S1desc'
        assert selenium.find_element_by_id(
            'budget_frm_starting_balance').get_attribute('value') == ''
        assert selenium.find_element_by_id(
            'budget_frm_group_starting_balance').is_displayed() is False
        assert selenium.find_element_by_id(
            'budget_frm_current_balance').get_attribute('value') == '1284.23'
        assert selenium.find_element_by_id(
            'budget_frm_group_current_balance').is_displayed()
        assert selenium.find_element_by_id('budget_frm_active').is_selected()


@pytest.mark.acceptance
@pytest.mark.usefixtures('class_refresh_db', 'refreshdb', 'testflask')
class TestEditStanding2(AcceptanceHelper):

    def test_1_populate_modal(self, base_url, selenium):
        selenium.get(base_url + '/budgets')
        link = selenium.find_element_by_xpath('//a[text()="Standing2 (5)"]')
        link.click()
        modal, title, body = self.get_modal_parts(selenium)
        self.assert_modal_displayed(modal, title, body)
        assert title.text == 'Edit Budget 5'
        assert selenium.find_element_by_id('budget_frm_name').get_attribute(
            'value') == 'Standing2'
        assert selenium.find_element_by_id(
            'budget_frm_type_periodic').is_selected() is False
        assert selenium.find_element_by_id(
            'budget_frm_type_standing').is_selected()
        assert selenium.find_element_by_id(
            'budget_frm_description').get_attribute('value') == 'S2desc'
        assert selenium.find_element_by_id(
            'budget_frm_starting_balance').get_attribute('value') == ''
        assert selenium.find_element_by_id(
            'budget_frm_group_starting_balance').is_displayed() is False
        assert selenium.find_element_by_id(
            'budget_frm_current_balance').get_attribute('value') == '9482.29'
        assert selenium.find_element_by_id(
            'budget_frm_group_current_balance').is_displayed()
        assert selenium.find_element_by_id('budget_frm_active').is_selected()


@pytest.mark.acceptance
@pytest.mark.usefixtures('class_refresh_db', 'refreshdb', 'testflask')
class TestDirectURLPeriodic1(AcceptanceHelper):

    def test_1_populate_modal(self, base_url, selenium):
        selenium.get(base_url + '/budgets/1')
        modal, title, body = self.get_modal_parts(selenium)
        self.assert_modal_displayed(modal, title, body)
        assert title.text == 'Edit Budget 1'
        assert selenium.find_element_by_id('budget_frm_name').get_attribute(
            'value') == 'Periodic1'
        assert selenium.find_element_by_id(
            'budget_frm_type_periodic').is_selected()
        assert selenium.find_element_by_id(
            'budget_frm_type_standing').is_selected() is False
        assert selenium.find_element_by_id(
            'budget_frm_description').get_attribute('value') == 'P1desc'
        assert selenium.find_element_by_id(
            'budget_frm_starting_balance').get_attribute('value') == '100'
        assert selenium.find_element_by_id(
            'budget_frm_group_starting_balance').is_displayed()
        assert selenium.find_element_by_id(
            'budget_frm_current_balance').get_attribute('value') == ''
        assert selenium.find_element_by_id(
            'budget_frm_group_current_balance').is_displayed() is False
        assert selenium.find_element_by_id('budget_frm_active').is_selected()
