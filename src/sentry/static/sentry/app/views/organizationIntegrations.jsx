import React from 'react';

import AsyncView from './asyncView';
import DropdownLink from '../components/dropdownLink';
import IndicatorStore from '../stores/indicatorStore';
import MenuItem from '../components/menuItem';
import OrganizationHomeContainer from '../components/organizations/homeContainer';
import {t} from '../locale';
import {sortArray} from '../utils';

export default class OrganizationIntegrations extends AsyncView {
  getEndpoints() {
    let {orgId} = this.props.params;
    return [
      ['itemList', `/organizations/${orgId}/integrations/`, {query: {status: ''}}],
      ['config', `/organizations/${orgId}/config/integrations/`]
    ];
  }

  deleteIntegration = integration => {
    // eslint-disable-next-line no-alert
    if (!confirm(t('Are you sure you want to remove this integration?'))) return;

    let indicator = IndicatorStore.add(t('Saving changes..'));
    this.api.request(
      `/organizations/${this.props.params.orgId}/integrations/${integration.id}/`,
      {
        method: 'DELETE',
        success: data => {
          let itemList = this.state.itemList;
          itemList.forEach(item => {
            if (item.id === data.id) {
              item.status = data.status;
            }
          });
          this.setState({
            itemList
          });
        },
        error: () => {
          IndicatorStore.add(t('An error occurred.'), 'error', {
            duration: 3000
          });
        },
        complete: () => {
          IndicatorStore.remove(indicator);
        }
      }
    );
  };

  cancelDelete = integration => {
    let indicator = IndicatorStore.add(t('Saving changes..'));
    this.api.request(
      `/organizations/${this.props.params.orgId}/integrations/${integration.id}/`,
      {
        method: 'PUT',
        data: {status: 'visible'},
        success: data => {
          let itemList = this.state.itemList;
          itemList.forEach(item => {
            if (item.id === data.id) {
              item.status = data.status;
            }
          });
          this.setState({
            itemList
          });
        },
        error: () => {
          IndicatorStore.add(t('An error occurred.'), 'error', {
            duration: 3000
          });
        },
        complete: () => {
          IndicatorStore.remove(indicator);
        }
      }
    );
  };

  onAddIntegration = integration => {
    let itemList = this.state.itemList;
    itemList.push(integration);
    this.setState({
      itemList: sortArray(itemList, item => item.name)
    });
  };

  launchAddIntegration = integration => {};

  getStatusLabel(integration) {
    switch (integration.status) {
      case 'pending_deletion':
        return 'Deletion Queued';
      case 'deletion_in_progress':
        return 'Deletion in Progress';
      case 'hidden':
        return 'Disabled';
      default:
        return null;
    }
  }

  getTitle() {
    return 'Repositories';
  }

  renderBody() {
    let itemList = this.state.itemList;

    return (
      <OrganizationHomeContainer>
        <div className="pull-right">
          <DropdownLink
            anchorRight
            className="btn btn-primary btn-sm"
            title={t('Add Integration')}>
            {this.state.config.providers.map(provider => {
              return (
                <MenuItem noAnchor={true} key={provider.id}>
                  <a onClick={this.launchAddIntegration.bind(this, provider)}>
                    {provider.name}
                  </a>
                </MenuItem>
              );
            })}
          </DropdownLink>
        </div>
        <h3 className="m-b-2">
          {t('Integrations')}
        </h3>
        {itemList.length > 0
          ? <div className="panel panel-default">
              <table className="table">
                <tbody>
                  {itemList.map(integration => {
                    return (
                      <tr key={integration.id}>
                        <td>
                          <strong>
                            {integration.name}
                          </strong>
                          {integration.status !== 'visible' &&
                            <small>
                              {' '}— {this.getStatusLabel(integration)}
                            </small>}
                          {integration.status === 'pending_deletion' &&
                            <small>
                              {' '}(
                              <a onClick={this.cancelDelete.bind(this, integration)}>
                                {t('Cancel')}
                              </a>
                              )
                            </small>}
                          <br />
                          <small>
                            {integration.name}
                          </small>
                        </td>
                        <td style={{width: 60}}>
                          {integration.status === 'visible'
                            ? <button
                                onClick={this.deleteIntegration.bind(this, integration)}
                                className="btn btn-default btn-xs">
                                <span className="icon icon-trash" />
                              </button>
                            : <button
                                onClick={this.deleteIntegration.bind(this, integration)}
                                disabled={true}
                                className="btn btn-default btn-xs btn-disabled">
                                <span className="icon icon-trash" />
                              </button>}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          : <div className="well blankslate align-center p-x-2 p-y-1">
              <div className="icon icon-lg icon-git-commit" />
              <h3>
                {t('Sentry is better with friends')}
              </h3>
              <p>
                {t(
                  'Integrations allow you to pull in things like repository data or sync with an external issue tracker.'
                )}
              </p>
              <p className="m-b-1">
                <a
                  className="btn btn-default"
                  href="https://docs.sentry.io/learn/integrations/">
                  Learn more
                </a>
              </p>
            </div>}
      </OrganizationHomeContainer>
    );
  }
}
