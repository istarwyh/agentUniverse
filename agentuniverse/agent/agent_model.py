# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/12 15:13
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: agent_model.py
"""Agent model class."""
from typing import Optional
from pydantic import BaseModel

from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.util.billing_center import BillingCenterInfo


class AgentModel(BaseModel):
    """The parent class of all agent models, containing only attributes."""

    info: Optional[dict] = dict()
    profile: Optional[dict] = dict()
    plan: Optional[dict] = dict()
    memory: Optional[dict] = dict()
    action: Optional[dict] = dict()
    work_pattern: Optional[dict] = dict()

    def billing_center_params(self):
        billing_center_info = BillingCenterInfo(agent_id=self.info.get("name"))
        return billing_center_info

    def llm_params(self) -> dict:
        """
        Returns:
            dict: The parameters for the LLM.
        """
        params = {}
        for key, value in self.profile.get('llm_model').items():
            if key == 'name' or key == 'prompt_processor':
                continue
            if key == 'model_name':
                params['model'] = value
            else:
                params[key] = value
        if ApplicationConfigManager().app_configer.use_billing_center:
            params["billing_center_params"] = self.billing_center_params()
        return params
