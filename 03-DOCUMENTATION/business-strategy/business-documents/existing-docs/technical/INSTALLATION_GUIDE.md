# 🚀 AIA CLI Installation Guide

## 📋 **Complete Installation Options for macOS**

The AIA CLI Ultimate AI Coding Assistant can be installed through multiple professional methods with secure JWT authentication.

---

## 🍎 **Method 1: Self-Contained macOS Installer (Recommended)**

### **Professional .pkg Installer**
```bash
# Build the installer package
./build_macos_installer.sh

# Install by double-clicking
# AIA-CLI-Installer.pkg
```

**Features:**
- ✅ Native macOS installer experience with GUI
- ✅ Code-signed and notarized for security
- ✅ Automatic dependency management
- ✅ Background services configuration
- ✅ Desktop application creation
- ✅ Automatic shell integration

---

## 🍺 **Method 2: Homebrew Installation**

### **Standard Homebrew Formula**
```bash
# Install from custom tap
brew tap aia-tech/aia-cli
brew install aia-cli

# Or when published to main Homebrew
brew install aia-cli
```

**Features:**
- ✅ Automatic dependency resolution
- ✅ Service management integration
- ✅ Easy updates with `brew upgrade aia-cli`
- ✅ Clean uninstall with `brew uninstall aia-cli`
- ✅ Standard developer workflow

---

## 🌐 **Method 3: One-Line Installer**

### **Instant Installation**
```bash
# Complete installation in one command
curl -sSL https://install.aia.tech | bash

# Or run local installer
./install-aia-ultimate.sh
```

**Features:**
- ✅ Instant deployment from anywhere
- ✅ Automatic system detection and configuration
- ✅ Complete setup including authentication
- ✅ Professional deployment ready

---

## 🔐 **Secure JWT Authentication Setup**

### **Authentication Features**
- **JWT Tokens**: Industry-standard with automatic refresh
- **macOS Keychain**: Secure credential storage (not files)
- **Device Fingerprinting**: Additional security layer
- **Enterprise-Grade**: SOC2, GDPR, HIPAA compliance ready
- **Audit Logging**: Complete security event tracking

### **Authentication Commands**
```bash
# Initial setup (one-time)
aia-auth setup                      # Interactive authentication setup

# Authentication management
aia-auth login                      # Secure login with email/password
aia-auth logout                     # Clear all credentials safely
aia-auth status                     # Check authentication status
aia-auth verify                     # Verify current JWT tokens
```

### **Demo Authentication**
For testing and demo purposes:
```bash
Email: demo@aia.tech
Password: demo123
```

---

## 🚀 **Usage After Installation**

### **Natural Language Interface**
```bash
# Just describe what you want to code
aia "implement secure user authentication with JWT tokens"
aia "analyze this project for security vulnerabilities"
aia "create React component for user dashboard"
aia "deploy to production with high security settings"
```

### **Autonomous Development**
```bash
# Complete autonomous development with sprint planning
aia "build complete e-commerce API with authentication and testing"

# Example output:
🚀 Autonomous Development Plan Created
- Total Sprints: 4
- Estimated Time: 15-18 hours
- Critical Decisions: 5 (require permission)
- Autonomous Tasks: 12 (auto-executed)

Proceed with autonomous implementation? [Y/n]
```

### **Continuous Conversations**
```bash
# Start ongoing coding conversation
aia "help me implement user management system"

# In interactive mode:
aia> Let's add JWT authentication
aia> Now add password reset functionality
aia> pause                           # Saves and exits to shell

# Resume later
aia continue                         # Resumes conversation

# End conversation
aia thanks                           # Graceful ending with summary
```

---

## 🏗️ **System Architecture**

### **Components Installed**
- **`aia`** - Main CLI command (globally accessible)
- **`aia-auth`** - Authentication management system
- **AIA Backend** - Multi-agent coordination service (localhost:8000)
- **DKG v3** - Knowledge graph service (localhost:8001)
- **Configuration** - User settings and session management

### **Directory Structure**
```
/usr/local/bin/aia              # Main CLI executable
/usr/local/bin/aia-auth         # Authentication system
~/.aia/                         # User configuration
  ├── sessions/                 # Conversation persistence
  ├── auth/                     # Authentication data
  ├── logs/                     # System logs
  └── config.yaml               # User preferences
```

---

## 🔧 **Troubleshooting**

### **Command Not Found**
```bash
# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Or restart terminal and try again
```

### **Authentication Issues**
```bash
# Reset authentication
aia-auth logout
aia-auth setup

# Check Keychain access
security find-generic-password -s "com.aia.cli"
```

### **Backend Services**
```bash
# Check service status
aia "show system status"

# Start services manually if needed
cd /Users/wXy/dev/Projects/aia
python3 -m uvicorn aia.main:app --host 0.0.0.0 --port 8000 &
```

---

## 🌟 **Enterprise Deployment**

### **For Organizations**
- **Code Signing**: Ready for enterprise certificate signing
- **Mass Deployment**: .pkg installer supports automated deployment
- **Configuration Management**: Centralized config templates
- **Security Compliance**: Meets enterprise security standards
- **Audit Logging**: Complete activity tracking

### **SSO Integration (Coming Soon)**
- Google Workspace authentication
- Microsoft Azure AD integration
- GitHub Enterprise authentication
- SAML 2.0 support for enterprise systems

---

## 📊 **Installation Verification**

### **Quick Test**
```bash
# Test basic functionality
aia help

# Test authentication system
aia-auth status

# Test AI capabilities
aia "analyze this project"

# Test system integration
aia "show system status"
```

### **Expected Results**
- ✅ Natural language processing working
- ✅ Beautiful Rich console interface
- ✅ Authentication system available
- ✅ Multi-agent coordination active
- ✅ Knowledge graph integration (2,472 atoms)

---

## 🎯 **Next Steps**

1. **Complete Installation**: Choose your preferred method above
2. **Setup Authentication**: Run `aia-auth setup` for full features
3. **Start Coding**: Use `aia "your coding request"` for AI assistance
4. **Explore Features**: Try autonomous development and sprint planning

**Welcome to the most advanced AI coding assistant ever created!** 🌟

---

*AIA CLI - Revolutionizing software development with autonomous AI intelligence*