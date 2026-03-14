#!/usr/bin/env ruby

#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

require 'fileutils'
require 'json'
require 'yaml'

def usage
  warn 'Usage: ruby tool/render_common_schema_json.rb <src_dir> <dest_dir>'
  exit 1
end

src_dir = ARGV[0]
dest_dir = ARGV[1]

usage if src_dir.nil? || dest_dir.nil?

FileUtils.mkdir_p(dest_dir)

Dir.children(src_dir).sort.each do |filename|
  source_path = File.join(src_dir, filename)
  next unless File.file?(source_path)

  case filename
  when /\.telepact\.yaml$/
    parsed = YAML.safe_load(
      File.read(source_path),
      permitted_classes: [],
      permitted_symbols: [],
      aliases: false
    )
    target_filename = filename.sub(/\.telepact\.yaml$/, '.telepact.json')
    target_path = File.join(dest_dir, target_filename)
    File.write(target_path, JSON.pretty_generate(parsed) + "\n")
  when /\.json$/
    FileUtils.cp(source_path, File.join(dest_dir, filename))
  end
end
