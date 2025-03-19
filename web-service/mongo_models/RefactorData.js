const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const DependencySchema = new Schema({
    name: { type: String, required: true },
    valid: { type: Boolean, required: true },
    fileContent: { type: String, required: true },
    weight: {
      name: {
        type: String,
        required: true
      },
      type: {
        type: String,
        required: true
      },
      alias: {
        type: String,
        required: false
      },
      source: {
        type: String,
        enum: ["Exporting", "Importing"],
        required: true
      }
    }
  });

// Magic Numbers Details Schema
const MagicNumbersDetailsSchema = new Schema({
    magic_number: { type: Schema.Types.Mixed, required: true }, // Can be number or string
    line_number: { type: Number, required: true }
  });
  
  // Base Refactor Request Schema
  const RefactorRequestSchema = new Schema({
    code: { type: String, required: true },
    refactor_type: { type: String, required: true },
    refactor_details: { type: Schema.Types.Mixed }
  }, { discriminatorKey: 'refactor_type' });
  
  // Refactor Response Schema
  const RefactorResponseSchema = new Schema({
    refactored_code: { type: String, required: true },
    dependencies: [DependencySchema],
    success: { type: Boolean, required: true },
    error: { type: String }
  });
  
  // Refactoring Data Schema
  const RefactoringDataSchema = new Schema({
    orginal_code: { type: String, required: true },
    refactored_code: { type: String },
    refactoring_type: { type: String },
    refactored_dependencies: [DependencySchema],
    time: { type: Date, default: Date.now, required: true },
    cascading_refactor: { type: Boolean },
    job_id: { type: String },
    ai_based: { type: Boolean },
    files_affected: [String],
    outdated: { type: Boolean },
    success: { type: Boolean, required: true },
    error: { type: String }
  });

  const RefactorSchema = new Schema({
    filePath: { type: String, required: true },
    refactorData: { 
      type: mongoose.Types.ObjectId,
      ref: 'RefactoringData',
      required: true
    }
  })
  
  // Create main models
  const RefactorRequest = mongoose.model('RefactorRequest', RefactorRequestSchema);
  const RefactorResponse = mongoose.model('RefactorResponse', RefactorResponseSchema);
  const RefactoringData = mongoose.model('RefactoringData', RefactoringDataSchema);
  const Refactor = mongoose.model('Refactor', RefactorSchema);
  // Create specific refactor request type models using discriminators
  const UnusedVariablesRefactorRequest = RefactorRequest.discriminator(
    'UnusedVariablesRefactorRequest',
    new Schema({
      unused_variables: { type: [String], required: true },
      dependencies: [DependencySchema]
    })
  );
  
  const MagicNumberRefactorRequest = RefactorRequest.discriminator(
    'MagicNumberRefactorRequest',
    new Schema({
      magic_numbers: [MagicNumbersDetailsSchema],
      dependencies: [DependencySchema]
    })
  );
  
  const InconsistentNamingRefactorRequest = RefactorRequest.discriminator(
    'InconsistentNamingRefactorRequest',
    new Schema({
      target_convention: { type: String, required: true },
      naming_convention: { type: String, required: true },
      dependencies: [DependencySchema]
    })
  );
  
  const UnreachableCodeRequest = RefactorRequest.discriminator(
    'UnreachableCodeRequest',
    new Schema({
      unreachable_code_lines: { type: [Number], required: true }
    })
  );
  
  const DeadCodeRefactorRequest = RefactorRequest.discriminator(
    'DeadCodeRefactorRequest',
    new Schema({
      entity_name: { type: String, required: true },
      entity_type: { type: String, required: true },
      dependencies: [DependencySchema]
    })
  );
  
  module.exports = {
    RefactorRequest,
    UnusedVariablesRefactorRequest,
    MagicNumberRefactorRequest,
    InconsistentNamingRefactorRequest,
    UnreachableCodeRequest,
    DeadCodeRefactorRequest,
    RefactorResponse,
    RefactoringData,
    Refactor
  };