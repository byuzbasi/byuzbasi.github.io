# frozen_string_literal: true

# Dart Sass can fail under Rosetta when an x86_64 Homebrew Ruby runs on an
# Apple Silicon Mac. In that narrow case bin/serve points the Ruby host at the
# checksum-verified ARM Dart Sass executable cached beside the site.
require "bundler/setup"
require "sass-embedded"

sass_root = ENV.fetch("BYUZBASI_SASS_ARM64_ROOT")
dart = File.join(sass_root, "lib/sass/dart-sass/src/dart")
snapshot = File.join(sass_root, "lib/sass/dart-sass/src/sass.snapshot")

unless File.executable?(dart) && File.file?(snapshot)
  raise "ARM Dart Sass runtime is incomplete at #{sass_root}"
end

cli = Sass.const_get(:CLI)
cli.send(:remove_const, :COMMAND)
cli.const_set(:COMMAND, [dart, snapshot].freeze)
