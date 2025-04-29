using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Text.Json;
using System.Management;
using Microsoft.Win32;

namespace KeyAuthClient
{
    public partial class MainForm : Form
    {
        private readonly HttpClient _httpClient;
        private string _token;
        private const string API_BASE_URL = "http://localhost:8000/api";

        public MainForm()
        {
            InitializeComponent();
            _httpClient = new HttpClient();
        }

        private async void btnLogin_Click(object sender, EventArgs e)
        {
            try
            {
                var loginData = new
                {
                    username = txtUsername.Text,
                    password = txtPassword.Text
                };

                var response = await _httpClient.PostAsync(
                    $"{API_BASE_URL}/auth/login",
                    new StringContent(JsonSerializer.Serialize(loginData), Encoding.UTF8, "application/json")
                );

                if (response.IsSuccessStatusCode)
                {
                    var result = await JsonSerializer.DeserializeAsync<LoginResponse>(await response.Content.ReadAsStreamAsync());
                    _token = result.access_token;
                    _httpClient.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", _token);
                    
                    MessageBox.Show("Login successful!");
                    EnableLicenseControls(true);
                }
                else
                {
                    MessageBox.Show("Login failed. Please check your credentials.");
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error: {ex.Message}");
            }
        }

        private async void btnActivate_Click(object sender, EventArgs e)
        {
            try
            {
                var hwid = GetHWID();
                var activateData = new
                {
                    license_key = txtLicenseKey.Text,
                    hwid = hwid
                };

                var response = await _httpClient.PostAsync(
                    $"{API_BASE_URL}/license/activate",
                    new StringContent(JsonSerializer.Serialize(activateData), Encoding.UTF8, "application/json")
                );

                if (response.IsSuccessStatusCode)
                {
                    var result = await JsonSerializer.DeserializeAsync<ActivateResponse>(await response.Content.ReadAsStreamAsync());
                    MessageBox.Show($"License activated successfully!\nType: {result.type}\nExpires: {result.expires_at}");
                }
                else
                {
                    MessageBox.Show("License activation failed. Please check your license key.");
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error: {ex.Message}");
            }
        }

        private async void btnValidate_Click(object sender, EventArgs e)
        {
            try
            {
                var hwid = GetHWID();
                var validateData = new
                {
                    license_key = txtLicenseKey.Text,
                    hwid = hwid
                };

                var response = await _httpClient.PostAsync(
                    $"{API_BASE_URL}/license/validate",
                    new StringContent(JsonSerializer.Serialize(validateData), Encoding.UTF8, "application/json")
                );

                if (response.IsSuccessStatusCode)
                {
                    var result = await JsonSerializer.DeserializeAsync<ValidateResponse>(await response.Content.ReadAsStreamAsync());
                    MessageBox.Show(result.valid
                        ? $"License is valid!\nType: {result.type}\nExpires: {result.expires_at}"
                        : $"License is not valid: {result.message}");
                }
                else
                {
                    MessageBox.Show("License validation failed.");
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error: {ex.Message}");
            }
        }

        private string GetHWID()
        {
            try
            {
                using (var mc = new ManagementClass("Win32_ComputerSystemProduct"))
                {
                    var moc = mc.GetInstances();
                    foreach (var mo in moc)
                    {
                        return mo["UUID"].ToString();
                    }
                }
            }
            catch
            {
                // Fallback to using processor ID if WMI fails
                using (var mc = new ManagementClass("Win32_Processor"))
                {
                    var moc = mc.GetInstances();
                    foreach (var mo in moc)
                    {
                        return mo.Properties["ProcessorId"].Value.ToString();
                    }
                }
            }
            return null;
        }

        private void EnableLicenseControls(bool enabled)
        {
            txtLicenseKey.Enabled = enabled;
            btnActivate.Enabled = enabled;
            btnValidate.Enabled = enabled;
        }

        private void InitializeComponent()
        {
            this.txtUsername = new TextBox();
            this.txtPassword = new TextBox();
            this.txtLicenseKey = new TextBox();
            this.btnLogin = new Button();
            this.btnActivate = new Button();
            this.btnValidate = new Button();

            // Form settings
            this.Text = "KeyAuth Client";
            this.Size = new System.Drawing.Size(400, 300);
            this.StartPosition = FormStartPosition.CenterScreen;

            // Username textbox
            this.txtUsername.Location = new System.Drawing.Point(100, 30);
            this.txtUsername.Size = new System.Drawing.Size(200, 20);
            this.txtUsername.PlaceholderText = "Username";

            // Password textbox
            this.txtPassword.Location = new System.Drawing.Point(100, 60);
            this.txtPassword.Size = new System.Drawing.Size(200, 20);
            this.txtPassword.PasswordChar = '*';
            this.txtPassword.PlaceholderText = "Password";

            // Login button
            this.btnLogin.Location = new System.Drawing.Point(150, 90);
            this.btnLogin.Size = new System.Drawing.Size(100, 30);
            this.btnLogin.Text = "Login";
            this.btnLogin.Click += new EventHandler(btnLogin_Click);

            // License key textbox
            this.txtLicenseKey.Location = new System.Drawing.Point(100, 150);
            this.txtLicenseKey.Size = new System.Drawing.Size(200, 20);
            this.txtLicenseKey.PlaceholderText = "License Key";
            this.txtLicenseKey.Enabled = false;

            // Activate button
            this.btnActivate.Location = new System.Drawing.Point(100, 180);
            this.btnActivate.Size = new System.Drawing.Size(100, 30);
            this.btnActivate.Text = "Activate";
            this.btnActivate.Enabled = false;
            this.btnActivate.Click += new EventHandler(btnActivate_Click);

            // Validate button
            this.btnValidate.Location = new System.Drawing.Point(200, 180);
            this.btnValidate.Size = new System.Drawing.Size(100, 30);
            this.btnValidate.Text = "Validate";
            this.btnValidate.Enabled = false;
            this.btnValidate.Click += new EventHandler(btnValidate_Click);

            // Add controls to form
            this.Controls.AddRange(new Control[] {
                txtUsername,
                txtPassword,
                txtLicenseKey,
                btnLogin,
                btnActivate,
                btnValidate
            });
        }

        private TextBox txtUsername;
        private TextBox txtPassword;
        private TextBox txtLicenseKey;
        private Button btnLogin;
        private Button btnActivate;
        private Button btnValidate;
    }

    public class LoginResponse
    {
        public string access_token { get; set; }
        public string token_type { get; set; }
        public int user_id { get; set; }
        public string username { get; set; }
        public bool is_admin { get; set; }
    }

    public class ActivateResponse
    {
        public string message { get; set; }
        public string type { get; set; }
        public DateTime? expires_at { get; set; }
    }

    public class ValidateResponse
    {
        public bool valid { get; set; }
        public string message { get; set; }
        public string type { get; set; }
        public DateTime? expires_at { get; set; }
    }

    static class Program
    {
        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new MainForm());
        }
    }
}