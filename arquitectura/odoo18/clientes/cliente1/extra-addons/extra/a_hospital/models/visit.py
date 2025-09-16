import random
from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import _


class Visit(models.Model):
    """
    Model representing a patient's visit within the hospital system.

    Visits are associated with patients, doctors, and may include diagnoses.
    This model supports tracking visit status, scheduling, and the assignment
    of doctors, including approvals by senior doctors.

    Fields:
        - patient_id (Many2one): The patient attending the visit.
        - doctor_id (Many2one): The doctor assigned to the visit.
        - initial_doctor_visit (Char): Initial doctor handling the visit.
        - doctor_approved (Char): Doctor who approved the visit, if required.
        - visit_status (Selection): Current status of the visit
        (e.g., scheduled, completed).
        - scheduled_date (Datetime): Scheduled date and time of the visit.
        - visit_date (Datetime): Actual date and time of the visit.
        - notes (Text): Additional notes about the visit.
        - diagnosis_ids (One2many): List of diagnoses made during the visit.
    """
    _name = 'a_hospital.visit'
    _description = 'Patient Visit'
    _order = 'create_date desc'  
    

    active = fields.Boolean(default=True)           # Поле для архівування

    patient_id = fields.Many2one(
        comodel_name='a_hospital.patient',
        string='Patient',
        required=True,
    )

    doctor_id = fields.Many2one(
        comodel_name='a_hospital.doctor',
        string='Doctor',
        required=True,
    )

    initial_doctor_visit = fields.Char(
        string="Initial doctor's visit",
        readonly=True,
    )

    doctor_approved = fields.Char(
        string='Doctor approved',
        readonly=True,
    )
    
    calendar_event_id = fields.Many2one('calendar.event', string='Calendar Event')

    visit_status = fields.Selection(
        [('scheduled', 'Scheduled'),
         ('completed', 'Completed'),
         ('canceled', 'Canceled')],
        required=True,
        default='scheduled',
    )

    scheduled_date = fields.Datetime(
        string="Scheduled Date & Time",
        required=True,
    )

    visit_date = fields.Datetime(
        string="Visit Date & Time",
    )

    notes = fields.Text()

    diagnosis_ids = fields.One2many(
        comodel_name='a_hospital.diagnosis',
        inverse_name='visit_id',
        string='Diagnoses'
    )
    
    def _create_calendar_event(self):
        """ Create calendar event for the visit """
        for visit in self:
            event = self.env['calendar.event'].create({
                'name': f'Visit: {visit.patient_id.first_name} with Dr. {visit.doctor_id.first_name}',
                'start': visit.scheduled_date,
                'stop': visit.visit_date or visit.scheduled_date + timedelta(hours=1),
                'description': visit.notes,
                'partner_ids': [(6, 0, [])],  # Add relevant partners if available
            })
            visit.calendar_event_id = event.id

    def _update_calendar_event(self):
        """ Update existing calendar event """
        for visit in self:
            if visit.calendar_event_id:
                visit.calendar_event_id.write({
                    'name': f'Visit: {visit.patient_id.first_name} with Dr. {visit.doctor_id.first_name}',
                    'start': visit.scheduled_date,
                    'stop': visit.visit_date or visit.scheduled_date + timedelta(hours=1),
                    'description': visit.notes,
                })

    def generate_random_date(self):
        """
        Generates a random date within the next 30 days.
        Returns:
            str: Formatted random date and time string.
        """
        today = datetime.today()
        days_offset = random.randint(0, 30)
        random_date = today + timedelta(days=days_offset)
        return random_date.strftime('%Y-%m-%d %H:%M:%S')

     
     

    @api.constrains('active')
    def _check_active(self):
        """
        Restricts archiving visits that have diagnoses.
        Raises:
            ValidationError: If attempting to archive
            a visit with linked diagnoses.
        """
        for visit in self:
            if not visit.active and visit.diagnosis_ids:
                raise ValidationError(_(
                    "Visits with diagnoses cannot be archived. "
                    "Please remove diagnoses before archiving."
                ))

    @api.constrains('patient_id', 'doctor_id', 'scheduled_date')
    def _check_duplicate_visit(self):
        """
        Prevents scheduling multiple visits for the same patient
        with the same doctor on the same day.
        Raises:
            ValidationError: If there are duplicate visits on the same day.
        """
        for visit in self:
            existing_visits = self.env['a_hospital.visit'].search_count([
                ('patient_id', '=', visit.patient_id.id),
                ('doctor_id', '=', visit.doctor_id.id),
                ('scheduled_date', '>=', visit.scheduled_date.date()),
                ('scheduled_date', '<',
                 visit.scheduled_date.date() + timedelta(days=1)),
                ('id', '!=', visit.id)])
            if existing_visits != 0:
                raise ValidationError(_(
                    "A patient cannot have multiple visits "
                    "with the same doctor on the same day."))

    def write(self, vals):
        """ Override write to update calendar event """
        result = super(Visit, self).write(vals)
        self._update_calendar_event()
        return result

    def unlink(self):
        """ Delete associated calendar event when visit is deleted """
        for visit in self:
            if visit.calendar_event_id:
                visit.calendar_event_id.unlink()
        return super(Visit, self).unlink()
    
    @api.model
    def create(self, vals):
        """ Override create to generate calendar event """
        visit = super(Visit, self).create(vals)
        visit._create_calendar_event()
        return visit
    
    
    @api.constrains('doctor_id', 'visit_status')
    def _onchange_doctor_id(self):
        """
        Sets the doctor's name in the doctor_approved field once
        the visit is completed and approved.
        Raises:
            ValidationError: If attempting to re-approve
            an already approved visit.
        """
        for visit in self:
            if visit.doctor_id:
                doctor = visit.doctor_id

                # Якщо лікар не інтерн і візит завершений
                if not doctor.is_intern and visit.visit_status == 'completed':
                    # Перевірка, чи поле doctor_approved вже заповнено
                    if not visit.doctor_approved:  # Якщо порожнє або None
                        visit.doctor_approved = doctor.display_name
                    else:
                        None
                        # raise ValidationError(_(
                        #     "Doctor has already been "
                        #     "approved for this visit."))
