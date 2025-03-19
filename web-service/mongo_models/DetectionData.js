const mongoose = require('mongoose');
const Schema = mongoose.Schema;

// GlobalVariable Schema
const GlobalVariableSchema = new Schema({
  variable_name: { type: String, required: true },
  variable_type: { type: String, required: true },
  class_or_function_name: { type: String }
});

// Import Schema
const ImportSchema = new Schema({
  name: { type: String, required: true },
  alias: { type: String },
  type: { type: String, required: true },
  module: { type: String }
});

// Condition Details Schema
const ConditionDetailsSchema = new Schema({
  line_range: { type: [Number], required: true },
  condition_code: { type: String, required: true },
  complexity_score: { type: Number, required: true },
  code_block: { type: String, required: true }
});

// Magic Numbers Details Schema
const MagicNumbersDetailsSchema = new Schema({
  magic_number: { type: Number, required: true },
  line_number: { type: Number, required: true }
});

// Parameter List Details Schema
const ParameterListDetailsSchema = new Schema({
  function_name: { type: String, required: true },
  parameters: { type: [String], required: true },
  long_parameter_count: { type: Number, required: true },
  long_parameter: { type: Boolean, required: true },
  line_number: { type: Number, required: true }
});

// Unused Variables Details Schema
const UnusedVariablesDetailsSchema = new Schema({
  variable_name: { type: String, required: true },
  line_number: { type: Number, required: true }
});

// Naming Convention Variables Schema
const NamingConventionVarsSchema = new Schema({
  variable: { type: String, required: true },
  line_number: { type: Number, required: true }
});

// Inconsistent Naming Details Schema
const InconsistentNamingDetailsSchema = new Schema({
  type: { type: String, required: true },
  total_count: { type: Number, required: true },
  type_count: { type: Number, required: true },
  vars: { type: [NamingConventionVarsSchema], required: true }
});

// Duplicates Schema
const DuplicatesSchema = new Schema({
  code: { type: String, required: true },
  start_line: { type: Number, required: true },
  end_line: { type: Number, required: true }
});

// Duplicate Code Details Schema
const DuplicateCodeDetailsSchema = new Schema({
  original_code: { type: String, required: true },
  start_line: { type: Number, required: true },
  end_line: { type: Number, required: true },
  duplicates: { type: [DuplicatesSchema], required: true },
  duplicate_count: { type: Number, required: true }
});

// Variable Conflict Analysis Schema
const VariableConflictAnalysisSchema = new Schema({
  variable: { type: String, required: true },
  assignments: { type: [[String, Number]], required: true },
  local_assignments: { type: [[String, Number]], required: true },
  usages: { type: [[String, Number]], required: true },
  conflicts: { type: [String], required: true },
  warnings: { type: [String], required: true }
});

// Sub Detection Response Schema
const SubDetectionResponseSchema = new Schema({
  success: { type: Boolean, required: true },
  error: { type: String },
  data: { type: Schema.Types.Mixed } // Can contain various types of data
});

// User Triggered Detection Schema
const UserTriggeredDetectionSchema = new Schema({
  data: { type: [Schema.Types.Mixed], required: true },
  time: { type: Date, required: true, default: Date.now },
  analysis_type: { type: String, required: true },
  job_id: { type: String, required: true },
  outdated: { type: Boolean, required: true, default: false },
  success: { type: Boolean, required: true },
  error: { type: String }
});

// Code Response Schema
const CodeResponseSchema = new Schema({
  code: { type: String },
  ast: { type: String },
  function_names: { type: [String] },
  class_details: { type: [Schema.Types.Mixed] },
  global_variables: { type: [GlobalVariableSchema] },
  is_main_block_present: { type: Boolean },
  imports: { type: Map, of: [ImportSchema] },
  is_standalone_file: { type: Boolean },
  success: { type: Boolean, required: true },
  error: { type: String }
});

// Detection Response Schema
const DetectionResponseSchema = new Schema({
  magic_numbers: { type: SubDetectionResponseSchema },
  duplicated_code: { type: SubDetectionResponseSchema },
  unused_variables: { type: SubDetectionResponseSchema },
  long_parameter_list: { type: SubDetectionResponseSchema },
  naming_convention: { type: SubDetectionResponseSchema },
  dead_code: { type: SubDetectionResponseSchema },
  unreachable_code: { type: SubDetectionResponseSchema },
  temporary_field: { type: SubDetectionResponseSchema },
  overly_complex_condition: { type: SubDetectionResponseSchema },
  global_conflict: { type: SubDetectionResponseSchema },
  user_triggered_detection: { type: [UserTriggeredDetectionSchema] },
  success: { type: Boolean, required: true },
  error: { type: String }
});

const DetectionSchema = new Schema({},
  {
    strict: false
  });



// File Response Schema
const FileResponseSchema = new Schema({
  fileName: { type: String, required: true },
  data: { type: Schema.Types.Mixed, required: true },
  success: { type: Boolean, required: true },
  error: { type: String }
}, { timestamps: true });

// Create and export the models
const GlobalVariable = mongoose.model('GlobalVariable', GlobalVariableSchema);
const Import = mongoose.model('Import', ImportSchema);
const CodeResponse = mongoose.model('CodeResponse', CodeResponseSchema);
const DetectionData = mongoose.model('DetectionData', DetectionResponseSchema);
const FileResponse = mongoose.model('FileResponse', FileResponseSchema);
const VariableConflictAnalysis = mongoose.model('VariableConflictAnalysis', VariableConflictAnalysisSchema);
const ConditionDetails = mongoose.model('ConditionDetails', ConditionDetailsSchema);
const MagicNumbersDetails = mongoose.model('MagicNumbersDetails', MagicNumbersDetailsSchema);
const ParameterListDetails = mongoose.model('ParameterListDetails', ParameterListDetailsSchema);
const UnusedVariablesDetails = mongoose.model('UnusedVariablesDetails', UnusedVariablesDetailsSchema);
const InconsistentNamingDetails = mongoose.model('InconsistentNamingDetails', InconsistentNamingDetailsSchema);
const DuplicateCodeDetails = mongoose.model('DuplicateCodeDetails', DuplicateCodeDetailsSchema);
const UserTriggeredDetection = mongoose.model('UserTriggeredDetection', UserTriggeredDetectionSchema);
const DetectionResponse = mongoose.model('DetectionResponse', DetectionSchema);

module.exports = {
  GlobalVariable,
  Import,
  CodeResponse,
  DetectionResponse,
  FileResponse,
  VariableConflictAnalysis,
  ConditionDetails,
  MagicNumbersDetails,
  ParameterListDetails,
  UnusedVariablesDetails,
  InconsistentNamingDetails,
  DuplicateCodeDetails,
  UserTriggeredDetection
};