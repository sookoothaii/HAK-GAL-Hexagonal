
            # === NEW TOOLS FOR VERSION 4.1 ===
            
            # Batch rename
            elif name == "batch_rename":
                if not self._is_write_allowed(arguments.get("auth_token", "")):
                    result = {"content": [{"type": "text", "text": "Write disabled or invalid token"}]}
                else:
                    path = arguments.get("path", ".")
                    pattern = arguments.get("pattern", "*")
                    rename_pattern = arguments.get("rename_pattern", "{name}_{num}{ext}")
                    dry_run = arguments.get("dry_run", True)
                    
                    try:
                        files = glob.glob(os.path.join(path, pattern))
                        operations = []
                        
                        for i, file_path in enumerate(files, 1):
                            if os.path.isfile(file_path):
                                dir_path = os.path.dirname(file_path)
                                filename = os.path.basename(file_path)
                                name, ext = os.path.splitext(filename)
                                
                                new_name = rename_pattern.replace("{name}", name)
                                new_name = new_name.replace("{ext}", ext)
                                new_name = new_name.replace("{num}", str(i).zfill(3))
                                new_name = new_name.replace("{date}", datetime.now().strftime("%Y%m%d"))
                                new_name = new_name.replace("{time}", datetime.now().strftime("%H%M%S"))
                                
                                new_path = os.path.join(dir_path, new_name)
                                operations.append((file_path, new_path))
                        
                        if dry_run:
                            text = f"DRY RUN - Would rename {len(operations)} files:\n\n"
                            for old, new in operations[:20]:
                                text += f"{os.path.basename(old)} → {os.path.basename(new)}\n"
                            if len(operations) > 20:
                                text += f"... and {len(operations) - 20} more"
                        else:
                            success = 0
                            for old_path, new_path in operations:
                                try:
                                    os.rename(old_path, new_path)
                                    success += 1
                                except:
                                    pass
                            text = f"Renamed {success}/{len(operations)} files successfully"
                        
                        result = {"content": [{"type": "text", "text": text}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            # Merge files
            elif name == "merge_files":
                if not self._is_write_allowed(arguments.get("auth_token", "")):
                    result = {"content": [{"type": "text", "text": "Write disabled or invalid token"}]}
                else:
                    files = arguments.get("files", [])
                    output = arguments.get("output", "")
                    separator = arguments.get("separator", "\n")
                    
                    try:
                        merged_content = []
                        for file_path in files:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                merged_content.append(f.read())
                        
                        final_content = separator.join(merged_content)
                        
                        with open(output, 'w', encoding='utf-8') as f:
                            f.write(final_content)
                        
                        text = f"Merged {len(files)} files into {output}\n"
                        text += f"Total size: {len(final_content):,} characters"
                        
                        result = {"content": [{"type": "text", "text": text}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
