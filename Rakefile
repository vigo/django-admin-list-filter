task :default => [:install]

desc "Remove/Delete build..."
task :clean do
  rm_rf %w(build dist)
  rm_rf Dir.glob("*.egg-info")
  puts "Build files are removed..."
end

desc "Build package"
task :build => [:clean] do
  system "python -m build"
end

namespace :upload do
  desc "Upload package to main distro (release)"
  task :main => [:build] do
    puts "Uploading package to MAIN distro..."
    system "twine upload --repository pypi dist/*"
  end

  desc "Upload package to test distro"
  task :test => [:build] do
    puts "Uploading package to TEST distro..."
    system "twine upload --repository testpypi dist/*"
  end
end

AVAILABLE_REVISIONS = ["major", "minor", "patch"]
desc "Bump version: #{AVAILABLE_REVISIONS.join(',')}"
task :bump, [:revision] do |t, args|
  args.with_defaults(revision: "patch")
  abort "Please provide valid revision: #{AVAILABLE_REVISIONS.join(',')}" unless AVAILABLE_REVISIONS.include?(args.revision)
  system "bumpversion #{args.revision}"
end

desc "Run tests"
task :test do
  system %{
    pytest -s --cov=src/dalf --cov-report=xml tests/testproject
  }
end
