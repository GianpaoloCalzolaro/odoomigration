from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestSurveyMultipleCertification(TransactionCase):
    """Test cases for Survey Multiple Certification module"""

    def setUp(self):
        super().setUp()
        self.Survey = self.env['survey.survey']
        self.Threshold = self.env['survey.certification.threshold']
        self.Wizard = self.env['survey.threshold.wizard']
        
        # Create test survey
        self.survey = self.Survey.create({
            'title': 'Test Survey',
            'certification_mode': 'multiple',
        })

    def test_survey_certification_mode(self):
        """Test that certification mode is properly set"""
        self.assertEqual(self.survey.certification_mode, 'multiple')
        
    def test_threshold_creation(self):
        """Test threshold creation and percentage_min computation"""
        threshold1 = self.Threshold.create({
            'survey_id': self.survey.id,
            'name': 'Bronze',
            'sequence': 10,
            'percentage_max': 60.0,
        })
        
        threshold2 = self.Threshold.create({
            'survey_id': self.survey.id,
            'name': 'Silver',
            'sequence': 20,
            'percentage_max': 80.0,
        })
        
        threshold3 = self.Threshold.create({
            'survey_id': self.survey.id,
            'name': 'Gold',
            'sequence': 30,
            'percentage_max': 100.0,
        })
        
        # Check percentage_min computation
        self.assertEqual(threshold1.percentage_min, 0.0)
        self.assertEqual(threshold2.percentage_min, 60.0)
        self.assertEqual(threshold3.percentage_min, 80.0)

    def test_wizard_action(self):
        """Test that wizard action returns correct values"""
        action = self.survey.action_open_threshold_wizard()
        
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_model'], 'survey.threshold.wizard')
        self.assertEqual(action['view_mode'], 'form')
        self.assertEqual(action['target'], 'new')
        self.assertEqual(action['context']['default_survey_id'], self.survey.id)

    def test_get_threshold_for_percentage(self):
        """Test threshold selection based on percentage"""
        # Create thresholds
        bronze = self.Threshold.create({
            'survey_id': self.survey.id,
            'name': 'Bronze',
            'sequence': 10,
            'percentage_max': 60.0,
        })
        
        silver = self.Threshold.create({
            'survey_id': self.survey.id,
            'name': 'Silver',
            'sequence': 20,
            'percentage_max': 80.0,
        })
        
        gold = self.Threshold.create({
            'survey_id': self.survey.id,
            'name': 'Gold',
            'sequence': 30,
            'percentage_max': 100.0,
        })
        
        # Test percentage to threshold mapping
        self.assertEqual(self.survey._get_threshold_for_percentage(50.0), bronze)
        self.assertEqual(self.survey._get_threshold_for_percentage(70.0), silver)
        self.assertEqual(self.survey._get_threshold_for_percentage(90.0), gold)
        self.assertEqual(self.survey._get_threshold_for_percentage(60.0), bronze)
        self.assertEqual(self.survey._get_threshold_for_percentage(80.0), silver)
        self.assertEqual(self.survey._get_threshold_for_percentage(100.0), gold)

    def test_wizard_workflow(self):
        """Test wizard creation and threshold generation"""
        wizard = self.Wizard.create({
            'survey_id': self.survey.id,
            'threshold_count': 3,
            'step': 'select'
        })
        
        # Test action_next
        action = wizard.action_next()
        self.assertEqual(wizard.step, 'config')
        self.assertEqual(len(wizard.threshold_line_ids), 3)
        
        # Check that lines have default names
        for i, line in enumerate(wizard.threshold_line_ids.sorted('sequence'), 1):
            self.assertEqual(line.name, f'Level {i}')

    def test_threshold_count_validation(self):
        """Test threshold count validation in wizard"""
        wizard = self.Wizard.create({
            'survey_id': self.survey.id,
            'threshold_count': 1,  # Invalid: too low
            'step': 'select'
        })
        
        with self.assertRaises(ValidationError):
            wizard.action_next()
            
        wizard.threshold_count = 16  # Invalid: too high
        with self.assertRaises(ValidationError):
            wizard.action_next()
