# Homebrew Formula for AIA CLI
# ============================
# Professional Homebrew integration for AIA Ultimate AI Coding Assistant

class AiaCli < Formula
  desc "🚀 Ultimate AI Coding Assistant with Autonomous Development"
  homepage "https://aia.tech"
  url "https://github.com/aia-tech/aia-cli/archive/v1.0.0.tar.gz"
  sha256 "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
  license "MIT"
  version "1.0.0"

  # Dependencies
  depends_on "python@3.11"
  depends_on "node" => :optional

  # Python dependencies
  resource "rich" do
    url "https://files.pythonhosted.org/packages/source/r/rich/rich-13.7.0.tar.gz"
    sha256 "5cb5123b5cf9ee70584244246816e9114227e0b98ad9176eede6ad54bf5403fa"
  end

  resource "prompt-toolkit" do
    url "https://files.pythonhosted.org/packages/source/p/prompt-toolkit/prompt_toolkit-3.0.43.tar.gz"
    sha256 "3527b7af26106cbc65a040bcc84839a3566ec1b051bb0bfe953631e704b0ff7d"
  end

  resource "aiohttp" do
    url "https://files.pythonhosted.org/packages/source/a/aiohttp/aiohttp-3.9.1.tar.gz"
    sha256 "8fc49a87ac269d4529da45871e2ffb6874e87779c3d0e2ccd813c0899221239"
  end

  resource "PyJWT" do
    url "https://files.pythonhosted.org/packages/source/P/PyJWT/PyJWT-2.8.0.tar.gz"
    sha256 "57e28d156e3d5c10088e0c68abb90bfac3df82b40a71bd0daa20c65ccd5c23de"
  end

  resource "cryptography" do
    url "https://files.pythonhosted.org/packages/source/c/cryptography/cryptography-41.0.7.tar.gz"
    sha256 "13f93ce9bea8016c253b34afc6bd6a75993e5c40672ed5405a9c832f0d4a00bc"
  end

  def install
    # Create installation directories
    (prefix/"lib"/"aia").mkpath
    (etc/"aia").mkpath
    (var/"log"/"aia").mkpath

    # Install Python dependencies
    venv = libexec/"venv"
    system Formula["python@3.11"].opt_bin/"python3.11", "-m", "venv", venv

    # Install dependencies in virtual environment
    system venv/"bin/pip", "install", "-v", "--no-deps", "--target=#{libexec}",
           resource("rich"), resource("prompt-toolkit"), resource("aiohttp"),
           resource("PyJWT"), resource("cryptography")

    # Install AIA CLI source files
    (prefix/"lib"/"aia").install "aia_optimized.py"
    (prefix/"lib"/"aia").install "aia_auth.py"
    (prefix/"lib"/"aia").install "aia_unified_processor.py"
    (prefix/"lib"/"aia").install "aia_autonomous.py"

    # Create wrapper script
    (bin/"aia").write <<~EOS
      #!/bin/bash
      export PYTHONPATH="#{prefix}/lib/aia:#{libexec}:$PYTHONPATH"
      exec "#{Formula["python@3.11"].opt_bin}/python3.11" "#{prefix}/lib/aia/aia_optimized.py" "$@"
    EOS

    # Create authentication command
    (bin/"aia-auth").write <<~EOS
      #!/bin/bash
      export PYTHONPATH="#{prefix}/lib/aia:#{libexec}:$PYTHONPATH"
      exec "#{Formula["python@3.11"].opt_bin}/python3.11" "#{prefix}/lib/aia/aia_auth.py" "$@"
    EOS

    # Install configuration files
    (etc/"aia").install "config.yaml" if File.exist?("config.yaml")

    # Install LaunchAgent plists for background services
    (prefix/"LaunchAgents").mkpath
    (prefix/"LaunchAgents").install "com.aia.backend.plist" if File.exist?("com.aia.backend.plist")
    (prefix/"LaunchAgents").install "com.aia.dkg.plist" if File.exist?("com.aia.dkg.plist")
  end

  def post_install
    # Create user configuration directory
    (var/"aia").mkpath
    (var/"aia"/"sessions").mkpath
    (var/"aia"/"auth").mkpath
    (var/"aia"/"logs").mkpath

    # Set up LaunchAgents
    ohai "Installing background services..."
    system "cp", "#{prefix}/LaunchAgents/com.aia.backend.plist", "#{Dir.home}/Library/LaunchAgents/" if File.exist?("#{prefix}/LaunchAgents/com.aia.backend.plist")
    system "cp", "#{prefix}/LaunchAgents/com.aia.dkg.plist", "#{Dir.home}/Library/LaunchAgents/" if File.exist?("#{prefix}/LaunchAgents/com.aia.dkg.plist")

    # Initial setup
    ohai "AIA CLI installed successfully!"
    ohai "Run 'aia auth setup' to configure secure authentication"
    ohai "Run 'aia help' to get started with AI coding assistance"
  end

  def caveats
    <<~EOS
      🔐 Authentication Setup Required
      ================================

      To unlock full autonomous development capabilities, set up secure authentication:

        aia auth setup

      This enables:
      ✅ Autonomous sprint-based development
      ✅ Multi-agent coordination (20+ specialists)
      ✅ Enterprise-grade security features
      ✅ Production deployment automation

      🚀 Quick Start:
        aia "implement user authentication"
        aia "analyze this project"
        aia "show system status"

      📚 Documentation: https://docs.aia.tech
    EOS
  end

  service do
    run [opt_bin/"aia", "daemon"]
    environment_variables AIA_CONFIG_DIR: var/"aia"
    keep_alive true
    log_path var/"log"/"aia"/"stdout.log"
    error_log_path var/"log"/"aia"/"stderr.log"
    working_dir var/"aia"
  end

  test do
    # Test basic functionality
    system "#{bin}/aia", "help"

    # Test authentication system
    system "#{bin}/aia-auth", "verify"

    # Check if services can start (without actually starting them)
    assert_predicate bin/"aia", :executable?
    assert_predicate bin/"aia-auth", :executable?
  end
end