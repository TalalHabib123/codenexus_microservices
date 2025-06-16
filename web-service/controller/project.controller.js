// const Scan = require('../mongo_models/Scan');
// const Project = require('../mongo_models/Project');
// const User = require('../mongo_models/User');
// const { processProjectsWithCodeSmells } = require('../utils/scanUtils.jsx');
// const { get } = require('mongoose');

// const projectController = {
//     create: async (req, res) => {
//         try {
//             const {title, description} = req.body
//             const project = new Project({
//                 title,
//                 description,
//                 Owner: req.user._id,
//                 members: [req.user._id],
//             });
//             await project.save();
//             console.log("Project created successfully", project);
//             res.status(201).json({message: "Project created successfully", project});
//         } catch (error) {
//             console.error(error);
//             res.status(500).json({message: "Internal server error", error});
//         }
//     },
//     getAll: async (req, res) => {
//         try {
//             const projects = await Project.find().populate('Owner').populate('members').populate('scans').populate({
//                 path: 'scans',
//                 populate: [
//                     { path: 'detect_id' },
//                     { path: 'refactor_id' }
//                 ]
//             });
            
//             // Process projects to calculate and update code smell counts
//             const processedProjects = await processProjectsWithCodeSmells(projects);
            
//             res.status(200).json(processedProjects);
//         } catch (error) {
//             console.error(error);
//             res.status(500).json({message: "Internal server error", error});
//         }
//     },

// getAllProjectInfos: async (req, res) => {
//     try {
//         const projects = await Project.find()
//             .populate('Owner')
//             .populate('members')
//             .populate('scans')
//             .populate({
//                 path: 'scans',
//                 populate: [
//                     { path: 'detect_id' },
//                     { path: 'refactor_id' }
//                 ]
//             });

//         // Process projects to calculate and update code smell counts
//         const processedProjects = await processProjectsWithCodeSmells(projects);

//         // Map processed projects to only return needed fields
//         const result = processedProjects.map(proj => {
//             const { _id, title, description, scans } = proj;
//             const totalScans = scans?.length || 0;

//             // Sort scans by date (newest first) to find the latest
//             const sortedScans = [...scans].sort((a, b) =>
//                 new Date(b.started_at || b.createdAt) - new Date(a.started_at || a.createdAt)
//             );

//             // Get the latest scan and its code smells
//             const latestScan = sortedScans[0] || {};
//             const codeSmellsInLatestScan = latestScan.total_issues_detected || 0;

//             // Count total refactors across all scans
//             let totalRefactors = 0;
//             scans.forEach(scan => {
//                 if (scan.refactor_id && Array.isArray(scan.refactor_id)) {
//                     totalRefactors += scan.refactor_id.length;
//                 }
//             });

//             return {
//                 _id,
//                 title,
//                 description,
//                 totalScans,
//                 codeSmellsInLatestScan,
//                 totalRefactors
//             };
//         });

//         res.status(200).json(result);
//     } catch (error) {
//         console.error(error);
//         res.status(500).json({ message: "Internal server error", error });
//     }
// },


//     getAllScans: async (req, res) => {
//         try {
//             const projectId = req.params.projectId;
//             const scans = await Scan.find({project_id: projectId}).populate('project_id');
//             res.status(200).json(scans);
//         } catch (error) {
//             console.error(error);
//             res.status(500).json({message: "Internal server error", error});
//         }
//     },

//     getScanById: async (req, res) => {
//         try {
//             const scanId = req.params.scanId;
//             const scan = await Scan.findById(scanId).populate('project_id');
//             if (!scan) {
//                 return res.status(404).json({message: "Scan not found"});
//             }
//             res.status(200).json(scan);
//         } catch (error) {
//             console.error(error);
//             res.status(500).json({message: "Internal server error", error});
//         }
//     },

//     getProjectById: async (req, res) => {
//         try {
//             const projectId = req.params.projectId;
//             const project = await Project
//             .findById(projectId).populate('Owner').populate('members')
//                 .populate({
//                 path: 'scans',
//                 populate: [
//                     {
//                         path: 'detect_id'
//                     },
//                     {
//                         path: 'refactor_id',
//                         populate: {
//                             path: 'refactorData'
//                         }
//                     }
//                 ]
//             });
//             if (!project) {
//                 return res.status(404).json({message: "Project not found"});
//             }
//             res.status(200).json(project);
//         } catch (error) {
//             console.error(error);
//             res.status(500).json({message: "error occurred"});
//         }
//     },

//    getLatestScan: async (req, res) => {
//         try {
//                const { projectId } = req.params;

//       // 1) Load the project and populate only the most recent scan
//       const project = await Project.findById(projectId).populate({
//         path: 'scans',
//         options: { sort: { started_at: -1 }, limit: 1 },
//         populate: [
//           { path: 'detect_id' },
//         ]
//       });

//       if (!project) {
//         return res.status(404).json({ message: 'Project not found' });
//       }
//       if (!project.scans.length) {
//         return res.status(404).json({ message: 'No scans for this project' });
//       }

//       // 2) The first (and only) element is the latest
//       const latestScan = project.scans[0];
//       res.status(200).json(latestScan);
//     } catch (error) {
//       console.error(error);
//       res.status(500).json({ message: 'Internal server error', error });
//     }
//   },

//   addMember: async (req, res) => {
//     try {
//         const projectId = req.params.projectId;
//         const userEmail = req.body.email;

//         //create user with given email if it doesn't exist 
//         let user = await User.findOne({ email:
//             userEmail
//         });
//         if (!user) {
//             user = new User({ email: userEmail });
//             await user.save();
//         }
//         const userId = user._id;

//         // Check if the user is already a member
//         const project = await Project.findById(projectId);
//         if (!project) {
//             return res.status(404).json({message: "Project not found"});
//         }
//         if (project.members.includes(userId)) {
//             return res.status(400).json({message: "User is already a member of this project"});
//         }

//         // Add the user to the project's members
//         project.members.push(userId);
//         await project.save();

//         res.status(200).json({message: "Member added successfully", project});
//     } catch (error) {
//         console.error(error);
//         res.status(500).json({message: "Internal server error", error});
//     }
//   },
//   removeMember: async (req, res) => {
//     try {
//         const projectId = req.params.projectId;
//         const userId = req.body;

//         // Check if the project exists
//         const project = await Project.findById(projectId);
//         if (!project) {
//             return res.status(404).json({message: "Project not found"});
//         }

//         // Check if the user is a member
//         if (!project.members.includes(userId)) {
//             return res.status(400).json({message: "User is not a member of this project"});
//         }

//         // Remove the user from the project's members
//         project.members = project.members.filter(member => member.toString() !== userId.toString());
//         await project.save();

//         res.status(200).json({message: "Member removed successfully", project});
//     } catch (error) {
//         console.error(error);
//         res.status(500).json({message: "Internal server error", error});
//     }
//   },
  
// }

// module.exports = projectController;



const Scan = require('../mongo_models/Scan');
const Project = require('../mongo_models/Project');
const User = require('../mongo_models/User');
const ProjectInvite = require('../mongo_models/ProjectInvite'); // New model for invites
const { processProjectsWithCodeSmells } = require('../utils/scanUtils.jsx');
const { sendInviteEmail } = require('../utils/emailService'); // Email utility
const { get } = require('mongoose');
const crypto = require('crypto');

const projectController = {
    create: async (req, res) => {
        try {
            const {title, description} = req.body
            const project = new Project({
                title,
                description,
                Owner: req.user._id,
                members: [req.user._id],
            });
            await project.save();
            console.log("Project created successfully", project);
            res.status(201).json({message: "Project created successfully", project});
        } catch (error) {
            console.error(error);
            res.status(500).json({message: "Internal server error", error});
        }
    },

    getAll: async (req, res) => {
        try {
            const projects = await Project.find().populate('Owner').populate('members').populate('scans').populate({
                path: 'scans',
                populate: [
                    { path: 'detect_id' },
                    { path: 'refactor_id' }
                ]
            });
            
            // Process projects to calculate and update code smell counts
            const processedProjects = await processProjectsWithCodeSmells(projects);
            
            res.status(200).json(processedProjects);
        } catch (error) {
            console.error(error);
            res.status(500).json({message: "Internal server error", error});
        }
    },

    getAllProjectInfos: async (req, res) => {
        try {
            const projects = await Project.find()
                .populate('Owner')
                .populate('members')
                .populate('scans')
                .populate({
                    path: 'scans',
                    populate: [
                        { path: 'detect_id' },
                        { path: 'refactor_id' }
                    ]
                });

            // Process projects to calculate and update code smell counts
            const processedProjects = await processProjectsWithCodeSmells(projects);

            // Map processed projects to only return needed fields
            const result = processedProjects.map(proj => {
                const { _id, title, description, scans } = proj;
                const totalScans = scans?.length || 0;

                // Sort scans by date (newest first) to find the latest
                const sortedScans = [...scans].sort((a, b) =>
                    new Date(b.started_at || b.createdAt) - new Date(a.started_at || a.createdAt)
                );

                // Get the latest scan and its code smells
                const latestScan = sortedScans[0] || {};
                const codeSmellsInLatestScan = latestScan.total_issues_detected || 0;

                // Count total refactors across all scans
                let totalRefactors = 0;
                scans.forEach(scan => {
                    if (scan.refactor_id && Array.isArray(scan.refactor_id)) {
                        totalRefactors += scan.refactor_id.length;
                    }
                });

                return {
                    _id,
                    title,
                    description,
                    totalScans,
                    codeSmellsInLatestScan,
                    totalRefactors
                };
            });

            res.status(200).json(result);
        } catch (error) {
            console.error(error);
            res.status(500).json({ message: "Internal server error", error });
        }
    },

    getAllScans: async (req, res) => {
        try {
            const projectId = req.params.projectId;
            const scans = await Scan.find({project_id: projectId}).populate('project_id');
            res.status(200).json(scans);
        } catch (error) {
            console.error(error);
            res.status(500).json({message: "Internal server error", error});
        }
    },

    getScanById: async (req, res) => {
        try {
            const scanId = req.params.scanId;
            const scan = await Scan.findById(scanId).populate('project_id');
            if (!scan) {
                return res.status(404).json({message: "Scan not found"});
            }
            res.status(200).json(scan);
        } catch (error) {
            console.error(error);
            res.status(500).json({message: "Internal server error", error});
        }
    },

    getProjectById: async (req, res) => {
        try {
            const projectId = req.params.projectId;
            const project = await Project
            .findById(projectId).populate('Owner').populate('members')
                .populate({
                path: 'scans',
                populate: [
                    {
                        path: 'detect_id'
                    },
                    {
                        path: 'refactor_id',
                        populate: {
                            path: 'refactorData'
                        }
                    }
                ]
            });
            if (!project) {
                return res.status(404).json({message: "Project not found"});
            }
            res.status(200).json(project);
        } catch (error) {
            console.error(error);
            res.status(500).json({message: "error occurred"});
        }
    },

    getLatestScan: async (req, res) => {
        try {
            const { projectId } = req.params;

            // 1) Load the project and populate only the most recent scan
            const project = await Project.findById(projectId).populate({
                path: 'scans',
                options: { sort: { started_at: -1 }, limit: 1 },
                populate: [
                    { path: 'detect_id' },
                ]
            });

            if (!project) {
                return res.status(404).json({ message: 'Project not found' });
            }
            if (!project.scans.length) {
                return res.status(404).json({ message: 'No scans for this project' });
            }

            // 2) The first (and only) element is the latest
            const latestScan = project.scans[0];
            res.status(200).json(latestScan);
        } catch (error) {
            console.error(error);
            res.status(500).json({ message: 'Internal server error', error });
        }
    },
    // Add this method to your project.controller.js

getProjectFiles: async (req, res) => {
    try {
        const { projectId } = req.params;
        
        // Find the project and return just the files array
        const project = await Project.findById(projectId).select('files title description');
        
        if (!project) {
            return res.status(404).json({ 
                message: "Project not found" 
            });
        }
        
        res.status(200).json({
            success: true,
            projectId: project._id,
            title: project.title,
            description: project.description,
            files: project.files || []
        });
        
    } catch (error) {
        console.error('Error getting project files:', error);
        res.status(500).json({ 
            message: "Internal server error", 
            error: error.message 
        });
    }
},

    // Enhanced invite/add member functionality
    inviteMember: async (req, res) => {
        try {
            const { projectId } = req.params;
            const { email } = req.body;
            const inviterId = req.user._id;

            // Validate email format
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                return res.status(400).json({ message: "Invalid email format" });
            }

            // Check if project exists and user is the owner
            const project = await Project.findById(projectId).populate('Owner');
            if (!project) {
                return res.status(404).json({ message: "Project not found" });
            }

            // Only owner can invite members
            // if (project.Owner._id.toString() !== inviterId.toString()) {
            //     return res.status(403).json({ message: "Only project owner can invite members" });
            // }

            // Check if user exists
            const existingUser = await User.findOne({ email: email.toLowerCase() });
            
            if (existingUser) {
                // User exists - check if already a member
                if (project.members.some(member => member.toString() === existingUser._id.toString())) {
                    return res.status(400).json({ message: "User is already a member of this project" });
                }

                // Add user directly to project
                project.members.push(existingUser._id);
                await project.save();

                // Send notification email to existing user
                try {
                    await sendInviteEmail({
                        email: existingUser.email,
                        projectTitle: project.title,
                        inviterName: project.Owner? project.Owner.username || project.Owner.email : "Unknown",
                        isExistingUser: true,
                        projectId: project._id
                    });
                } catch (emailError) {
                    console.error('Failed to send notification email:', emailError);
                    // Don't fail the request if email fails
                }

                return res.status(200).json({ 
                    message: "User added to project successfully",
                    userExists: true,
                    user: {
                        _id: existingUser._id,
                        email: existingUser.email,
                        username: existingUser.username
                    }
                });
            } else {
                // User doesn't exist - create invitation
                
                // Check if there's already a pending invitation for this email and project
                const existingInvite = await ProjectInvite.findOne({
                    email: email.toLowerCase(),
                    projectId: projectId,
                    status: 'pending'
                });

                if (existingInvite) {
                    return res.status(400).json({ message: "Invitation already sent to this email" });
                }

                // Generate invitation token
                const inviteToken = crypto.randomBytes(32).toString('hex');
                const inviteExpiry = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); // 7 days

                // Create invitation record
                const invitation = new ProjectInvite({
                    email: email.toLowerCase(),
                    projectId: projectId,
                    invitedBy: inviterId,
                    inviteToken: inviteToken,
                    expiresAt: inviteExpiry,
                    status: 'pending'
                });

                await invitation.save();

                // Send invitation email
                try {
                    await sendInviteEmail({
                        email: email.toLowerCase(),
                        projectTitle: project.title,
                        inviterName: project.Owner? project.Owner.username || project.Owner.email : "Unknown",
                        isExistingUser: false,
                        inviteToken: inviteToken,
                        projectId: project._id
                    });
                } catch (emailError) {
                    console.error('Failed to send invitation email:', emailError);
                    // Delete the invitation if email fails
                    await ProjectInvite.findByIdAndDelete(invitation._id);
                    return res.status(500).json({ message: "Failed to send invitation email" });
                }

                return res.status(200).json({ 
                    message: "Invitation sent successfully",
                    userExists: false,
                    inviteToken: inviteToken // You might want to remove this in production
                });
            }

        } catch (error) {
            console.error('Error in inviteMember:', error);
            res.status(500).json({ message: "Internal server error", error: error.message });
        }
    },

    // Accept invitation endpoint
    acceptInvitation: async (req, res) => {
        try {
            const { token } = req.params;
            
            // Find the invitation
            const invitation = await ProjectInvite.findOne({
                inviteToken: token,
                status: 'pending',
                expiresAt: { $gt: new Date() }
            }).populate('projectId');

            if (!invitation) {
                return res.status(404).json({ message: "Invalid or expired invitation" });
            }

            // Check if user exists now (they might have registered after invitation)
            let user = await User.findOne({ email: invitation.email });
            
            if (!user) {
                // User still doesn't exist - they need to register first
                return res.status(400).json({ 
                    message: "Please register an account first",
                    redirectToRegister: true,
                    email: invitation.email
                });
            }

            // Add user to project
            const project = await Project.findById(invitation.projectId);
            if (!project.members.includes(user._id)) {
                project.members.push(user._id);
                await project.save();
            }

            // Mark invitation as accepted
            invitation.status = 'accepted';
            invitation.acceptedAt = new Date();
            await invitation.save();

            res.status(200).json({ 
                message: "Successfully joined the project",
                project: {
                    _id: project._id,
                    title: project.title,
                    description: project.description
                }
            });

        } catch (error) {
            console.error('Error accepting invitation:', error);
            res.status(500).json({ message: "Internal server error", error: error.message });
        }
    },

    // Get pending invitations for a project
    getPendingInvitations: async (req, res) => {
        try {
            const { projectId } = req.params;
            const userId = req.user._id || "";

            // Check if user is project owner
            const project = await Project.findById(projectId);
            if (!project) {
                return res.status(404).json({ message: "Project not found" });
            }

            if (project.Owner.toString() !== userId.toString()) {
                return res.status(403).json({ message: "Only project owner can view invitations" });
            }

            const pendingInvitations = await ProjectInvite.find({
                projectId: projectId,
                status: 'pending',
                expiresAt: { $gt: new Date() }
            }).select('email createdAt expiresAt');

            res.status(200).json(pendingInvitations);

        } catch (error) {
            console.error('Error getting pending invitations:', error);
            res.status(500).json({ message: "Internal server error", error: error.message });
        }
    },

    // Cancel/revoke invitation
    cancelInvitation: async (req, res) => {
        try {
            const { projectId } = req.params;
            const { email } = req.body;
            const userId = req.user._id;

            // Check if user is project owner
            const project = await Project.findById(projectId);
            if (!project) {
                return res.status(404).json({ message: "Project not found" });
            }

            if (project.Owner.toString() !== userId.toString()) {
                return res.status(403).json({ message: "Only project owner can cancel invitations" });
            }

            // Find and cancel the invitation
            const invitation = await ProjectInvite.findOneAndUpdate(
                {
                    email: email.toLowerCase(),
                    projectId: projectId,
                    status: 'pending'
                },
                {
                    status: 'cancelled',
                    cancelledAt: new Date()
                },
                { new: true }
            );

            if (!invitation) {
                return res.status(404).json({ message: "Invitation not found" });
            }

            res.status(200).json({ message: "Invitation cancelled successfully" });

        } catch (error) {
            console.error('Error cancelling invitation:', error);
            res.status(500).json({ message: "Internal server error", error: error.message });
        }
    },

    removeMember: async (req, res) => {
        try {
            const { projectId } = req.params;
            const { userId } = req.body;
            const requesterId = req.user._id;

            // Check if the project exists
            const project = await Project.findById(projectId);
            if (!project) {
                return res.status(404).json({ message: "Project not found" });
            }

            // Only owner can remove members (or users can remove themselves)
            if (project.Owner.toString() !== requesterId.toString() && userId !== requesterId.toString()) {
                return res.status(403).json({ message: "Only project owner can remove members" });
            }

            // Can't remove the owner
            if (project.Owner.toString() === userId) {
                return res.status(400).json({ message: "Cannot remove project owner" });
            }

            // Check if the user is a member
            if (!project.members.some(member => member.toString() === userId)) {
                return res.status(400).json({ message: "User is not a member of this project" });
            }

            // Remove the user from the project's members
            project.members = project.members.filter(member => member.toString() !== userId);
            await project.save();

            res.status(200).json({ message: "Member removed successfully" });
        } catch (error) {
            console.error('Error removing member:', error);
            res.status(500).json({ message: "Internal server error", error: error.message });
        }
    }
};

module.exports = projectController;