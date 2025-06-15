const nodemailer = require('nodemailer');

// Configure your email service here
const transporter = nodemailer.createTransport({
    // Example for Gmail
    service: 'gmail',
    auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS // Use app-specific password for Gmail
    }
    
    // Alternative SMTP configuration
    // host: process.env.SMTP_HOST,
    // port: process.env.SMTP_PORT,
    // secure: false,
    // auth: {
    //     user: process.env.SMTP_USER,
    //     pass: process.env.SMTP_PASS
    // }
});

const sendInviteEmail = async ({ email, projectTitle, inviterName, isExistingUser, inviteToken, projectId }) => {
    try {
        const frontendUrl = process.env.FRONTEND_URL || 'http://localhost:3000';
        
        let subject, htmlContent;

        if (isExistingUser) {
            // Email for existing users
            subject = `You've been added to "${projectTitle}"`;
            htmlContent = `
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                        .header { background-color: #007bff; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
                        .content { background-color: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }
                        .button { 
                            display: inline-block; 
                            padding: 12px 24px; 
                            background-color: #007bff; 
                            color: white; 
                            text-decoration: none; 
                            border-radius: 4px; 
                            margin: 20px 0; 
                        }
                        .footer { text-align: center; margin-top: 20px; color: #666; font-size: 12px; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>Welcome to the Project!</h1>
                        </div>
                        <div class="content">
                            <h2>Hello!</h2>
                            <p><strong>${inviterName}</strong> has added you as a member to the project <strong>"${projectTitle}"</strong>.</p>
                            <p>You can now access the project and view all its scans and information.</p>
                            <p>
                                <a href="${frontendUrl}/project/${projectId}/overview" class="button">
                                    View Project
                                </a>
                            </p>
                            <p>If you have any questions, please contact the project owner.</p>
                        </div>
                        <div class="footer">
                            <p>This email was sent because you were added to a project. If you believe this was sent in error, please contact the project owner.</p>
                        </div>
                    </div>
                </body>
                </html>
            `;
        } else {
            // Email for new users (invitation)
            subject = `You're invited to join "${projectTitle}"`;
            htmlContent = `
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                        .header { background-color: #28a745; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
                        .content { background-color: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }
                        .button { 
                            display: inline-block; 
                            padding: 12px 24px; 
                            background-color: #28a745; 
                            color: white; 
                            text-decoration: none; 
                            border-radius: 4px; 
                            margin: 20px 0; 
                        }
                        .footer { text-align: center; margin-top: 20px; color: #666; font-size: 12px; }
                        .highlight { background-color: #fff3cd; padding: 10px; border-radius: 4px; margin: 15px 0; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>You're Invited!</h1>
                        </div>
                        <div class="content">
                            <h2>Hello!</h2>
                            <p><strong>${inviterName}</strong> has invited you to join the project <strong>"${projectTitle}"</strong>.</p>
                            
                            <div class="highlight">
                                <p><strong>To accept this invitation:</strong></p>
                                <ol>
                                    <li>Click the button below to accept the invitation</li>
                                    <li>If you don't have an account, you'll be asked to register first</li>
                                    <li>Once registered/logged in, you'll automatically be added to the project</li>
                                </ol>
                            </div>
                            
                            <p>
                                <a href="${frontendUrl}/accept-invitation/${inviteToken}" class="button">
                                    Accept Invitation
                                </a>
                            </p>
                            
                            <p><strong>This invitation will expire in 7 days.</strong></p>
                            
                            <p>If you have any questions about this project, please contact ${inviterName}.</p>
                        </div>
                        <div class="footer">
                            <p>This invitation was sent to ${email}. If you believe this was sent in error, you can safely ignore this email.</p>
                        </div>
                    </div>
                </body>
                </html>
            `;
        }

        const mailOptions = {
            from: process.env.EMAIL_FROM || process.env.EMAIL_USER,
            to: email,
            subject: subject,
            html: htmlContent
        };

        const result = await transporter.sendMail(mailOptions);
        console.log('Email sent successfully:', result.messageId);
        return result;

    } catch (error) {
        console.error('Error sending email:', error);
        throw error;
    }
};

// Optional: Send reminder email for pending invitations
const sendReminderEmail = async ({ email, projectTitle, inviterName, inviteToken, projectId }) => {
    try {
        const frontendUrl = process.env.FRONTEND_URL || 'http://localhost:3000';
        
        const subject = `Reminder: You're invited to join "${projectTitle}"`;
        const htmlContent = `
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background-color: #ffc107; color: #333; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
                    .content { background-color: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }
                    .button { 
                        display: inline-block; 
                        padding: 12px 24px; 
                        background-color: #ffc107; 
                        color: #333; 
                        text-decoration: none; 
                        border-radius: 4px; 
                        margin: 20px 0; 
                    }
                    .footer { text-align: center; margin-top: 20px; color: #666; font-size: 12px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Reminder: Project Invitation</h1>
                    </div>
                    <div class="content">
                        <h2>Don't forget!</h2>
                        <p>You have a pending invitation to join the project <strong>"${projectTitle}"</strong> from <strong>${inviterName}</strong>.</p>
                        
                        <p>
                            <a href="${frontendUrl}/accept-invitation/${inviteToken}" class="button">
                                Accept Invitation
                            </a>
                        </p>
                        
                        <p><strong>This invitation will expire soon.</strong></p>
                    </div>
                    <div class="footer">
                        <p>This is a reminder email. If you're not interested, you can safely ignore this email.</p>
                    </div>
                </div>
            </body>
            </html>
        `;

        const mailOptions = {
            from: process.env.EMAIL_FROM || process.env.EMAIL_USER,
            to: email,
            subject: subject,
            html: htmlContent
        };

        const result = await transporter.sendMail(mailOptions);
        console.log('Reminder email sent successfully:', result.messageId);
        return result;

    } catch (error) {
        console.error('Error sending reminder email:', error);
        throw error;
    }
};

module.exports = {
    sendInviteEmail,
    sendReminderEmail
};