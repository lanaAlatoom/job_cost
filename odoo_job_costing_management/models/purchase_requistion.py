# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import Warning, UserError



class PurchaseRequisition(models.Model):
    _inherit = 'material.purchase.requisition'

    # @api.multi
    @api.onchange('project_id')
    def onchange_project_task(self):
        for rec in self:
            # rec.project_id = rec.task_id.project_id.id
            rec.analytic_account_id = rec.project_id.analytic_account_id.id
            rec.task_user_id = rec.task_id.user_ids[0].id if rec.task_id.user_ids else False
            rec.task_id.project_id = rec.project_id

    # @api.multi
    @api.depends('requisition_line_ids',
                 'requisition_line_ids.product_id',
                 'requisition_line_ids.product_id.boq_type')
    def compute_equipment_machine(self):
        eqp_machine_total = 0.0
        work_resource_total = 0.0
        work_cost_package_total = 0.0
        subcontract_total = 0.0
        for rec in self:
            for line in rec.requisition_line_ids:
                if line.product_id.boq_type == 'eqp_machine':
                    eqp_machine_total += line.product_id.standard_price * line.qty
                if line.product_id.boq_type == 'worker_resource':
                    work_resource_total += line.product_id.standard_price * line.qty
                if line.product_id.boq_type == 'work_cost_package':
                    work_cost_package_total += line.product_id.standard_price * line.qty
                if line.product_id.boq_type == 'subcontract':
                    subcontract_total += line.product_id.standard_price * line.qty
            rec.equipment_machine_total = eqp_machine_total
            rec.worker_resource_total = work_resource_total
            rec.work_cost_package_total = work_cost_package_total
            rec.subcontract_total = subcontract_total

    #     #@api.multi
    #     @api.depends('purchase_order_ids')
    #     def _purchase_order_count(self):
    #         for rec in self:
    #             rec.purchase_order_count = len(rec.purchase_order_ids)


    jop_costing_id = fields.Many2one('job.costing', string='Costing' )

    project_id = fields.Many2one('project.project', string='Construction Project', required=True)

    @api.onchange('project_id')
    def onchange_project_id(self):
        if self.project_id:
            job_costing = self.env['job.costing'].search([('project_id', '=', self.project_id.id)], limit=1)
            if job_costing:
                self.jop_costing_id = job_costing
            else:
                self.jop_costing_id = False

    task_id = fields.Many2one(
        'project.task',
        string='Task / Job Order',
        required=False,

    )

    task_user_id = fields.Many2one(
        'res.users',
        # related='task_id.user_id',
        # related='task_id.activity_user_id',
        string='Task / Job Order User'
    )

    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
    )
    #     analytic_account_id = fields.Many2one(
    #         'account.analytic.account',
    #         string='Analytic Account',
    #     )
    purchase_order_ids = fields.Many2many(
        'purchase.order',
        string='Purchase Orders',
    )
    #     purchase_order_count = fields.Integer(
    #         compute='_purchase_order_count',
    #         string="Purchase Orders",
    #         store=True,
    #     )
    equipment_machine_total = fields.Float(
        compute='compute_equipment_machine',
        string='Equipment / Machinery Cost',
        store=True,
    )
    worker_resource_total = fields.Float(
        compute='compute_equipment_machine',
        string='Worker / Resource Cost',
        store=True,
    )
    work_cost_package_total = fields.Float(
        compute='compute_equipment_machine',
        string='Work Cost Package',
        store=True,
    )
    subcontract_total = fields.Float(
        compute='compute_equipment_machine',
        string='Subcontract Cost',
        store=True,
    )

