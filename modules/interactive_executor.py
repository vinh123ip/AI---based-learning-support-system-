import asyncio
import subprocess
import tempfile
import os
import sys
from typing import Dict, List, Optional, Tuple
import uuid
import threading
import queue
import time

class InteractiveExecutor:
    def __init__(self):
        self.sessions: Dict[str, 'InteractiveSession'] = {}
        self.cleanup_interval = 300  # 5 minutes
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """Start background thread to cleanup old sessions"""
        def cleanup():
            while True:
                time.sleep(self.cleanup_interval)
                current_time = time.time()
                expired_sessions = []
                
                for session_id, session in self.sessions.items():
                    if current_time - session.last_activity > self.cleanup_interval:
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    self.cleanup_session(session_id)
        
        thread = threading.Thread(target=cleanup, daemon=True)
        thread.start()
    
    def create_session(self) -> str:
        """Create a new interactive session"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = InteractiveSession(session_id)
        return session_id
    
    def cleanup_session(self, session_id: str):
        """Clean up a session"""
        if session_id in self.sessions:
            self.sessions[session_id].cleanup()
            del self.sessions[session_id]
    
    async def execute_with_inputs(self, code: str, inputs: List[str]) -> Dict:
        """Execute code with predefined inputs for input() calls"""
        try:
            # Create a temporary file with the code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                # Modify code to handle input() calls
                modified_code = self._modify_code_for_inputs(code, inputs)
                f.write(modified_code)
                temp_file = f.name
            
            # Execute the code
            try:
                # Set environment variables for UTF-8 encoding
                env = os.environ.copy()
                env['PYTHONIOENCODING'] = 'utf-8'
                env['PYTHONUNBUFFERED'] = '1'
                
                process = await asyncio.create_subprocess_exec(
                    sys.executable, temp_file,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=env
                )
                
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10.0)
                
                stdout_text = stdout.decode('utf-8', errors='replace').strip() if stdout else ''
                stderr_text = stderr.decode('utf-8', errors='replace').strip() if stderr else ''
                
                # Extract prompt from stderr if available
                prompt_message = ''
                if '__PROMPT__:' in stderr_text:
                    import re
                    match = re.search(r'__PROMPT__:(.*?)__END__', stderr_text)
                    if match:
                        prompt_message = match.group(1)
                        # Remove prompt markers from stderr
                        stderr_text = re.sub(r'__PROMPT__:.*?__END__\n?', '', stderr_text)
                
                # Check if more input is needed
                needs_more_input = ('EOFError: More input required' in stderr_text or 
                                  'EOFError: Input required but not provided' in stderr_text)
                
                return {
                    'success': True,
                    'result': {
                        'output': stdout_text,
                        'error': stderr_text if not needs_more_input else '',
                        'return_code': process.returncode,
                        'needs_input': needs_more_input,
                        'prompt': prompt_message if needs_more_input else ''
                    }
                }
                
            except asyncio.TimeoutError:
                return {
                    'success': False,
                    'result': {
                        'error': 'Code execution timed out (10 seconds limit)',
                        'return_code': -1,
                        'needs_input': False
                    }
                }
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file)
                except:
                    pass
                    
        except Exception as e:
            return {
                'success': False,
                'result': {
                    'error': f'Execution error: {str(e)}',
                    'return_code': -1,
                    'needs_input': False
                }
            }
    
    def _modify_code_for_inputs(self, code: str, inputs: List[str]) -> str:
        """Modify code to replace input() calls with predefined inputs"""
        if not inputs:
            # If no inputs provided, check if code needs inputs
            if 'input(' in code:
                return f"""
import sys
import json

def _mock_input(prompt=''):
    # Send prompt info to stderr for frontend to catch (DON'T print to stdout)
    print("__PROMPT__:" + prompt + "__END__", file=sys.stderr, flush=True)
    raise EOFError('Input required but not provided')

# Replace built-in input with our mock
input = _mock_input

{code}
"""
        
        # Create input iterator
        input_setup = f"""
import sys
import json
_input_values = {inputs!r}
_input_index = 0

def _mock_input(prompt=''):
    global _input_index
    if _input_index >= len(_input_values):
        # Send prompt info to stderr for frontend to catch (DON'T print to stdout)
        print("__PROMPT__:" + prompt + "__END__", file=sys.stderr, flush=True)
        raise EOFError('More input required')
    value = _input_values[_input_index]
    _input_index += 1
    # KHÔNG in prompt để tránh lặp lại trong output
    # Frontend sẽ tự hiển thị prompt và input từ phía client
    return str(value)

# Replace built-in input with our mock
input = _mock_input
"""
        
        return input_setup + '\n' + code
    
    async def execute_interactive(self, code: str, session_id: Optional[str] = None) -> Dict:
        """Execute code interactively, handling input() calls"""
        if session_id and session_id in self.sessions:
            session = self.sessions[session_id]
            session.last_activity = time.time()
            return await session.execute(code)
        else:
            # Create new session for one-time execution
            session = InteractiveSession(str(uuid.uuid4()))
            return await session.execute(code)


class InteractiveSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.last_activity = time.time()
        self.process = None
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        self.is_running = False
        self.waiting_for_input = False
    
    async def execute(self, code: str) -> Dict:
        """Execute code in this session"""
        try:
            # For now, just execute code normally
            # In a full implementation, we'd maintain a persistent Python process
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_file = f.name
            
            try:
                env = os.environ.copy()
                env['PYTHONIOENCODING'] = 'utf-8'
                env['PYTHONUNBUFFERED'] = '1'
                
                process = await asyncio.create_subprocess_exec(
                    sys.executable, temp_file,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=env
                )
                
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=5.0)
                
                return {
                    'success': True,
                    'result': {
                        'output': stdout.decode('utf-8', errors='replace').strip() if stdout else '',
                        'error': stderr.decode('utf-8', errors='replace').strip() if stderr else '',
                        'return_code': process.returncode,
                        'needs_input': False
                    }
                }
                
            except asyncio.TimeoutError:
                return {
                    'success': False,
                    'result': {
                        'error': 'Code execution timed out (5 seconds limit)',
                        'return_code': -1,
                        'needs_input': False
                    }
                }
            finally:
                try:
                    os.unlink(temp_file)
                except:
                    pass
                    
        except Exception as e:
            return {
                'success': False,
                'result': {
                    'error': f'Execution error: {str(e)}',
                    'return_code': -1,
                    'needs_input': False
                }
            }
    
    def cleanup(self):
        """Clean up session resources"""
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=1)
            except:
                try:
                    self.process.kill()
                except:
                    pass
        self.is_running = False


# Global executor instance
interactive_executor = InteractiveExecutor() 