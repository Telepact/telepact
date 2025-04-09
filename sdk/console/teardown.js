import { execSync } from 'child_process';

export default function () {
  try {
    console.log('Stopping and removing Docker container...');
    execSync('docker rm -f telepact_console_test', { stdio: 'inherit' });
  } catch (error) {
    console.error('Error during teardown:', error.message);
  }
}
