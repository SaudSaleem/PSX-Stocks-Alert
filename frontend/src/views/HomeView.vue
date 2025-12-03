<template>
  <div class="home-container flex flex-col">
    <div class="flex flex-row gap-2 flex-wrap items-center">
      <Button @click="showDrawer = true" style="width: 200px;">Open Drawer</Button>
      <Button @click="showCreateAlertDialog = true" style="width: 200px;">Create Alert</Button>
      <Button @click="showCalculateSharesDialog = true" style="width: 200px;">Calculate Shares</Button>
      <Button @click="showAddInvestmentDialog = true" style="width: 200px;">Manage Funds</Button>
      <Button @click="openInvestmentHistory" style="width: 200px;" severity="secondary">Investment History</Button>
      <Button @click="openPhoneNumbersDialog" style="width: 200px;" severity="help">WhatsApp Numbers</Button>
      <Button @click="openEmailRecipientsDialog" style="width: 200px;" severity="success">Email Recipients</Button>
      <Button @click="showTestWhatsAppDialog = true" style="width: 200px;" severity="info">Test WhatsApp</Button>
      
      <!-- Complexity Toggle -->
      <div class="flex items-center gap-2 ml-auto">
        <label for="complexity-toggle" class="font-semibold">Show Advanced Fields:</label>
        <input 
          id="complexity-toggle" 
          type="checkbox" 
          v-model="showComplexity" 
          class="toggle-checkbox"
        />
      </div>
    </div>
    <!-- Portfolio Summary Card -->
    <Card v-if="user && portfolioPnl" class="portfolio-card mt-8">
      <template #content>
        <div class="portfolio-summary">
          <h3>Portfolio Summary</h3>
          <div class="portfolio-stats">
            <div class="stat-item">
              <span class="stat-label">Total Investment:</span>
              <span class="stat-value">PKR {{ formatCurrency(portfolioPnl.total_investment) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Invested in Shares:</span>
              <span class="stat-value">PKR {{ formatCurrency(portfolioPnl.invested_in_shares) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Cash Available:</span>
              <span class="stat-value">PKR {{ formatCurrency(portfolioPnl.cash_available) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Current Value:</span>
              <span class="stat-value">PKR {{ formatCurrency(portfolioPnl.current_value) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Profit/Loss:</span>
              <span class="stat-value" :class="portfolioPnl.pnl >= 0 ? 'positive-change' : 'negative-change'">
                PKR {{ formatCurrency(portfolioPnl.pnl) }} ({{ portfolioPnl.pnl_percentage.toFixed(2) }}%)
              </span>
            </div>
          </div>
        </div>
      </template>
    </Card>

    <Card v-if="user" class="welcome-card mt-8">
      <template #content>
        <div class="alerts-section">
          <Button @click="fetchAlerts" class="mb-4">Refresh Alerts</Button>
          <DataTable :value="alerts" stripedRows paginator :rows="10" tableStyle="min-width: 160rem">
            <!-- Basic Columns -->
            <Column field="ticker" header="Ticker" sortable></Column>
            <Column field="buy_price" header="Buy Price" sortable></Column>
            <Column field="current_price" header="Current Price" sortable></Column>
            <Column field="change_percentage" header="Change %" sortable>
              <template #body="slotProps">
                <span :class="slotProps.data.change_percentage >= 0 ? 'positive-change' : 'negative-change'">
                  {{ slotProps.data.change_percentage }}%
                </span>
              </template>
            </Column>
            <Column header="Status">
              <template #body="slotProps">
                <div class="status-indicators">
                  <span v-if="slotProps.data.is_sl_hit" class="status-badge sl-hit">SL Hit</span>
                  <span v-if="slotProps.data.is_tp1_hit" class="status-badge tp-hit">TP1 Hit</span>
                  <span v-if="slotProps.data.is_tp2_hit" class="status-badge tp-hit">TP2 Hit</span>
                  <span v-if="slotProps.data.is_tp3_hit" class="status-badge tp-hit">TP3 Hit</span>
                  <span v-if="slotProps.data.is_box_break_hit" class="status-badge box-break">Box Break</span>
                  <span v-if="slotProps.data.is_dip_buy_hit" class="status-badge dip-buy">Dip Buy</span>
                  <span v-if="slotProps.data.is_percentage_sl_hit" class="status-badge sl-hit">Percentage SL Hit</span>
                  <span v-if="slotProps.data.is_percentage_tp_hit" class="status-badge tp-hit">Percentage TP Hit</span>
                  <span v-if="slotProps.data.is_trailing_stop_hit" class="status-badge tp-hit">Trailing Stop Hit</span>
                </div>
              </template>
            </Column>
            <Column field="sl" header="SL"></Column>
            <Column field="tp1" header="TP1"></Column>
            <Column field="tp2" header="TP2"></Column>
            <Column field="shares" header="Shares"></Column>
            <Column field="tp3" header="TP3"></Column>
            
            <!-- Advanced Columns (shown when showComplexity is true) -->
            <Column v-if="showComplexity" field="percentage_tp" header="TP %"></Column>
            <Column v-if="showComplexity" field="percentage_sl" header="SL %"></Column>
            <Column  field="dip_buy" header="Dip Buy"></Column>
            <Column v-if="showComplexity" field="box_break" header="Box Break"></Column>
            <Column v-if="showComplexity" field="notes" header="Notes"></Column>
            <Column v-if="showComplexity" field="total_alerts_sent" header="Total Alerts Sent"></Column>
            <Column v-if="showComplexity" field="date_added" header="Created At">
              <template #body="slotProps">
                {{ new Date(slotProps.data.date_added).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }) }}
              </template>
            </Column>
            <Column v-if="showComplexity" field="date_modified" header="Last Modified">
              <template #body="slotProps">
                {{ new Date(slotProps.data.date_modified).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }) }}
              </template>
            </Column>
            
            <!-- Action Columns (always shown) -->
            <Column field="update" header="Update">
              <template #body="slotProps">
                <Button @click="showUpdateAlertDialog = true; selectedAlert = {...slotProps.data}" label="Update" severity="warning" />
              </template>
            </Column>
            <Column field="delete" header="Delete">
              <template #body="slotProps">
                <Button @click="showDeleteAlertDialog = true; selectedAlert = slotProps.data" label="Delete" severity="danger" />
              </template>
            </Column>
          </DataTable>
        </div>
      </template>
    </Card>
    <Toast />
    <Drawer v-model:visible="showDrawer" :header="`Welcome, ${user?.name}`" :modal="true">
      <div class="user-info">
        <h3>Your information:</h3>
        <p><strong>Email:</strong> {{ user?.email }}</p>
        <p v-if="user?.name"><strong>Name:</strong> {{ user?.name }}</p>
        <p v-if="user?.phone"><strong>Phone:</strong> {{ user?.phone }}</p>
        <div v-if="portfolioPnl" class="portfolio-info">
          <h4>Portfolio Summary:</h4>
          <p><strong>Total Investment:</strong> PKR {{ formatCurrency(portfolioPnl.total_investment) }}</p>
          <p><strong>Invested in Shares:</strong> PKR {{ formatCurrency(portfolioPnl.invested_in_shares) }}</p>
          <p><strong>Cash Available:</strong> PKR {{ formatCurrency(portfolioPnl.cash_available) }}</p>
          <p><strong>Current Value:</strong> PKR {{ formatCurrency(portfolioPnl.current_value) }}</p>
          <p><strong>Profit/Loss:</strong> 
            <span :class="portfolioPnl.pnl >= 0 ? 'positive-change' : 'negative-change'">
              PKR {{ formatCurrency(portfolioPnl.pnl) }} ({{ portfolioPnl.pnl_percentage.toFixed(2) }}%)
            </span>
          </p>
        </div>
        
        <!-- Notification Preferences -->
        <div class="notification-preferences">
          <h4>Notification Preferences:</h4>
          <div class="preference-item">
            <label class="flex items-center gap-2">
              <input 
                type="checkbox" 
                v-model="notificationPreferences.email_notifications_enabled"
                @change="updateNotificationPreferences('email_notifications_enabled', notificationPreferences.email_notifications_enabled)"
                class="toggle-checkbox"
              />
              <span>📧 Email Notifications</span>
            </label>
          </div>
          <div class="preference-item">
            <label class="flex items-center gap-2">
              <input 
                type="checkbox" 
                v-model="notificationPreferences.whatsapp_notifications_enabled"
                @change="updateNotificationPreferences('whatsapp_notifications_enabled', notificationPreferences.whatsapp_notifications_enabled)"
                class="toggle-checkbox"
              />
              <span>📱 WhatsApp Notifications</span>
            </label>
          </div>
        </div>
      </div>
      <div class="actions">
        <Button label="Logout" @click="logout" />
      </div>
    </Drawer>
    <Dialog v-model:visible="showCreateAlertDialog" :header="`Create Alert`" :modal="true" style="width: 50vw;">
      <div class="create-alert-form flex flex-wrap gap-2">
        <!-- Basic Fields -->
        <div class="flex flex-col gap-2 flex-1">
          <label for="ticker">Ticker</label>
          <Select v-model="alert.ticker" filter clearIcon :options="tickers" optionLabel="symbol" optionValue="symbol"
            placeholder="Select Ticker" class="flex-1">
          </Select>
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="buy_price">Buy Price</label>
          <InputNumber v-model="alert.buy_price" placeholder="Buy Price" class="flex-1" :minFractionDigits="2" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="shares">Shares</label>
          <InputNumber v-model="alert.shares" placeholder="Shares" class="flex-1" :minFractionDigits="2" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="sl">SL</label>
          <InputNumber v-model="alert.sl" placeholder="SL" class="flex-1" :minFractionDigits="2" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="tp1">TP1</label>
          <InputNumber v-model="alert.tp1" placeholder="TP1" class="flex-1" :minFractionDigits="2" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="tp2">TP2</label>
          <InputNumber v-model="alert.tp2" placeholder="TP2" class="flex-1" :minFractionDigits="2" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="tp3">TP3</label>
          <InputNumber v-model="alert.tp3" placeholder="TP3" class="flex-1" :minFractionDigits="2" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="notes">Notes</label>
          <InputText v-model="alert.notes" placeholder="Notes" class="flex-1" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
            <label for="dip_buy">Dip Buy</label>
            <InputNumber v-model="alert.dip_buy" placeholder="Dip Buy" class="flex-1" :minFractionDigits="2" />
        </div>
        <!-- Advanced Fields (shown when showComplexity is true) -->
        <template v-if="showComplexity">
          <div class="flex flex-col gap-2 flex-1">
            <label for="percentage_tp">TP %</label>
            <InputNumber v-model="alert.percentage_tp" placeholder="TP %" class="flex-1" :minFractionDigits="2" />
          </div>
          <div class="flex flex-col gap-2 flex-1">
            <label for="percentage_sl">SL %</label>
            <InputNumber v-model="alert.percentage_sl" placeholder="SL %" class="flex-1" :minFractionDigits="2" />
          </div>
          <div class="flex flex-col gap-2 flex-1">
            <label for="box_break">Box Break</label>
            <InputNumber v-model="alert.box_break" placeholder="Box Break" class="flex-1" :minFractionDigits="2" />
          </div>
          <div class="flex flex-col gap-2 flex-1">
            <label for="trailing_stop_percentage">Trailing Stop %</label>
            <InputNumber v-model="alert.trailing_stop_percentage" placeholder="Trailing Stop %" class="flex-1" :minFractionDigits="2" />
          </div>
        </template>
      </div>
      <div class="w-full flex justify-center mt-3">
        <Button @click="createAlert" label="Create Alert" />
      </div>
    </Dialog>
    <Dialog v-model:visible="showDeleteAlertDialog" :header="`Delete Alert`" :modal="true" style="width: 50vw;">
      <div class="flex flex-col gap-2">
        <p style="text-align: center;">Are you sure you want to delete this alert?</p>
        <Button @click="deleteAlert(selectedAlert?.id)" class="mt-5" style="width: 100px; margin: 0 auto;" label="Delete" severity="danger" />
      </div>
    </Dialog>
    <Dialog v-model:visible="showUpdateAlertDialog" :header="`Update Alert`" :modal="true" style="width: 50vw;">
      <div class="update-alert-form flex flex-wrap gap-2">
        <!-- Basic Fields -->
        <div class="flex flex-col gap-2 flex-1">
          <label for="ticker">Ticker</label>
          <Select v-model="selectedAlert.ticker" disabled filter clearIcon :options="tickers" optionLabel="symbol" optionValue="symbol"
            placeholder="Select Ticker" class="flex-1">
          </Select>
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="buy_price">Buy Price</label>
          <InputNumber v-model="selectedAlert.buy_price" placeholder="Buy Price" class="flex-1" :minFractionDigits="2" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="shares">Shares</label>
          <InputNumber v-model="selectedAlert.shares" placeholder="Shares" class="flex-1" :minFractionDigits="2" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="sl">SL</label>
          <InputNumber v-model="selectedAlert.sl" placeholder="SL" class="flex-1" :minFractionDigits="2" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="tp1">TP1</label>
          <InputNumber v-model="selectedAlert.tp1" placeholder="TP1" class="flex-1" :minFractionDigits="2" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="tp2">TP2</label>
          <InputNumber v-model="selectedAlert.tp2" placeholder="TP2" class="flex-1" :minFractionDigits="2" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="tp3">TP3</label>
          <InputNumber v-model="selectedAlert.tp3" placeholder="TP3" class="flex-1" :minFractionDigits="2" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="notes">Notes</label>
          <InputText v-model="selectedAlert.notes" placeholder="Notes" class="flex-1" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
            <label for="dip_buy">Dip Buy</label>
            <InputNumber v-model="selectedAlert.dip_buy" placeholder="Dip Buy" class="flex-1" :minFractionDigits="2" />
          </div>
        <!-- Advanced Fields (shown when showComplexity is true) -->
        <template v-if="showComplexity">
          <div class="flex flex-col gap-2 flex-1">
            <label for="percentage_tp">TP %</label>
            <InputNumber v-model="selectedAlert.percentage_tp" placeholder="TP %" class="flex-1" :minFractionDigits="2" />
          </div>
          <div class="flex flex-col gap-2 flex-1">
            <label for="percentage_sl">SL %</label>
            <InputNumber v-model="selectedAlert.percentage_sl" placeholder="SL %" class="flex-1" :minFractionDigits="2" />
          </div>
          <div class="flex flex-col gap-2 flex-1">
            <label for="box_break">Box Break</label>
            <InputNumber v-model="selectedAlert.box_break" placeholder="Box Break" class="flex-1" :minFractionDigits="2" />
          </div>
          <div class="flex flex-col gap-2 flex-1">
            <label for="trailing_stop_percentage">Trailing Stop %</label>
            <InputNumber v-model="selectedAlert.trailing_stop_percentage" placeholder="Trailing Stop %" class="flex-1" :minFractionDigits="2" />
          </div>
        </template>
      </div>
      <div class="w-full flex justify-center mt-3">
        <Button @click="updateAlert" label="Update Alert" />
      </div>
    </Dialog>
    <Dialog v-model:visible="showCalculateSharesDialog" :header="`Calculate Shares`" :modal="true" style="width: 40vw;">
      <div class="calculate-shares-form flex flex-col flex-wrap gap-2">
        <div class="flex flex-col gap-2 flex-1">
          <label for="calc_ticker">Ticker</label>
          <Select v-model="calcShares.ticker" filter clearIcon :options="tickers" optionLabel="symbol" optionValue="symbol"
            placeholder="Select Ticker" class="flex-1" @change="onCalcTickerChange" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="calc_price">Current Price</label>
          <InputNumber :model-value="calcShares.current_price"  placeholder="Current Price" class="flex-1" @input="(event) => calculateShares(event.value, 'current_price')" :minFractionDigits="2"/>
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="calc_amount">Amount</label>
          <InputNumber :model-value="calcShares.amount" mode="currency" currency="PKR" placeholder="Amount to Invest" class="flex-1" @input="(event) => calculateShares(event.value, 'amount')" :minFractionDigits="2" />
        </div>
        <div class="flex flex-col items-center gap-2 flex-1 font-bold">
          <label for="calc_result ">Shares</label>
          <span class="flex-1">{{ calcShares.result }}</span>
        </div>
      </div>
    </Dialog>
    <Dialog v-model:visible="showAddInvestmentDialog" :header="`Manage Investment`" :modal="true" style="width: 40vw;">
      <div class="add-investment-form flex flex-col gap-4">
        <div class="flex flex-col gap-2">
          <label for="transaction_type">Transaction Type</label>
          <Select v-model="investment.transaction_type" :options="transactionTypes" optionLabel="label" optionValue="value" placeholder="Select Type" class="flex-1" />
  </div>
        <div class="flex flex-col gap-2">
          <label for="investment_amount">Amount (PKR)</label>
          <InputNumber v-model="investment.amount" mode="currency" currency="PKR" placeholder="Amount" class="flex-1" :minFractionDigits="2" />
        </div>
        <div class="flex flex-col gap-2">
          <label for="investment_description">Description (Optional)</label>
          <InputText v-model="investment.description" placeholder="e.g., Monthly investment, Profit withdrawal" class="flex-1" />
        </div>
        <div class="w-full flex justify-center mt-3">
          <Button @click="addInvestment" :label="investment.transaction_type === 'add' ? 'Add Funds' : 'Withdraw Funds'" />
        </div>
      </div>
    </Dialog>
    <Dialog v-model:visible="showInvestmentHistoryDialog" :header="`Investment History`" :modal="true" style="width: 60vw;">
      <div class="investment-history">
        <DataTable :value="investments" stripedRows paginator :rows="10">
          <Column field="date_added" header="Date" sortable>
            <template #body="slotProps">
              {{ new Date(slotProps.data.date_added).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) }}
            </template>
          </Column>
          <Column field="transaction_type" header="Type" sortable>
            <template #body="slotProps">
              <span :class="slotProps.data.transaction_type === 'add' ? 'transaction-add' : 'transaction-withdraw'">
                {{ slotProps.data.transaction_type === 'add' ? 'Add Funds' : 'Withdraw Funds' }}
              </span>
            </template>
          </Column>
          <Column field="amount" header="Amount" sortable>
            <template #body="slotProps">
              <span :class="slotProps.data.transaction_type === 'add' ? 'positive-change' : 'negative-change'">
                {{ slotProps.data.transaction_type === 'add' ? '+' : '-' }} PKR {{ formatCurrency(slotProps.data.amount) }}
              </span>
            </template>
          </Column>
          <Column field="description" header="Description"></Column>
        </DataTable>
      </div>
    </Dialog>
    <Dialog v-model:visible="showPhoneNumbersDialog" :header="`WhatsApp Alert Numbers`" :modal="true" style="width: 60vw;">
      <div class="phone-numbers-section">
        <div class="add-phone-form flex gap-3 mb-4">
          <InputText v-model="newPhoneNumber.phone_number" placeholder="e.g., +923001234567" class="flex-1" />
          <InputText v-model="newPhoneNumber.label" placeholder="Label (optional, e.g., Personal)" class="flex-1" />
          <Button @click="addPhoneNumber" label="Add Number" icon="pi pi-plus" />
        </div>
        <div class="help-text mb-4">
          <p class="text-sm text-gray-600">
            📱 <strong>Format:</strong> Use international format with country code (e.g., +923001234567 for Pakistan)<br/>
            💬 <strong>For testing:</strong> First, send "join" to whatsapp:+14155238886 from your WhatsApp to join the sandbox
          </p>
        </div>
        <DataTable :value="phoneNumbers" stripedRows>
          <Column field="phone_number" header="Phone Number"></Column>
          <Column field="label" header="Label"></Column>
          <Column field="is_active" header="Status">
            <template #body="slotProps">
              <span :class="slotProps.data.is_active ? 'status-active' : 'status-inactive'">
                {{ slotProps.data.is_active ? 'Active' : 'Inactive' }}
              </span>
            </template>
          </Column>
          <Column field="date_added" header="Added On">
            <template #body="slotProps">
              {{ new Date(slotProps.data.date_added).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) }}
            </template>
          </Column>
          <Column field="actions" header="Actions">
            <template #body="slotProps">
              <div class="flex gap-2">
                <Button 
                  @click="togglePhoneStatus(slotProps.data)" 
                  :label="slotProps.data.is_active ? 'Deactivate' : 'Activate'" 
                  :severity="slotProps.data.is_active ? 'warning' : 'success'"
                  size="small"
                />
                <Button 
                  @click="deletePhoneNumber(slotProps.data.id)" 
                  label="Delete" 
                  severity="danger"
                  size="small"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    </Dialog>
    <Dialog v-model:visible="showEmailRecipientsDialog" :header="`Email Alert Recipients`" :modal="true" style="width: 60vw;">
      <div class="email-recipients-section">
        <div class="add-email-form flex gap-3 mb-4">
          <InputText v-model="newEmailRecipient.email" placeholder="e.g., example@email.com" class="flex-1" type="email" />
          <InputText v-model="newEmailRecipient.label" placeholder="Label (optional, e.g., Personal)" class="flex-1" />
          <Button @click="addEmailRecipient" label="Add Email" icon="pi pi-plus" />
        </div>
        <div class="help-text mb-4">
          <p class="text-sm text-gray-600">
            📧 <strong>Email Alerts:</strong> Add email addresses to receive stock alerts<br/>
            💡 <strong>Note:</strong> If no recipients are added, alerts will be sent to your login email by default
          </p>
        </div>
        <DataTable :value="emailRecipients" stripedRows>
          <Column field="email" header="Email Address"></Column>
          <Column field="label" header="Label"></Column>
          <Column field="is_active" header="Status">
            <template #body="slotProps">
              <span :class="slotProps.data.is_active ? 'status-active' : 'status-inactive'">
                {{ slotProps.data.is_active ? 'Active' : 'Inactive' }}
              </span>
            </template>
          </Column>
          <Column field="date_added" header="Added On">
            <template #body="slotProps">
              {{ new Date(slotProps.data.date_added).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) }}
            </template>
          </Column>
          <Column field="actions" header="Actions">
            <template #body="slotProps">
              <div class="flex gap-2">
                <Button 
                  @click="toggleEmailStatus(slotProps.data)" 
                  :label="slotProps.data.is_active ? 'Deactivate' : 'Activate'" 
                  :severity="slotProps.data.is_active ? 'warning' : 'success'"
                  size="small"
                />
                <Button 
                  @click="deleteEmailRecipient(slotProps.data.id)" 
                  label="Delete" 
                  severity="danger"
                  size="small"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    </Dialog>
    <Dialog v-model:visible="showTestWhatsAppDialog" :header="`Test WhatsApp Alert`" :modal="true" style="width: 50vw;">
      <div class="test-whatsapp-section">
        <div class="flex flex-col gap-4">
          <div class="info-box">
            <p class="text-sm">
              <strong>📱 Testing Instructions:</strong><br/>
              1. Make sure you've joined the Twilio sandbox (send "join your-code" to +14155238886)<br/>
              2. Add your phone number in WhatsApp Numbers section<br/>
              3. Use this form to send a test alert to verify everything works
            </p>
          </div>
          
          <div class="flex flex-col gap-2">
            <label for="test_phone">Send to Phone Number</label>
            <Select v-model="testWhatsApp.selectedPhone" :options="phoneNumbers" 
              optionLabel="phone_number" optionValue="phone_number" 
              placeholder="Select a phone number" class="flex-1">
              <template #option="slotProps">
                <div class="flex justify-between w-full">
                  <span>{{ slotProps.option.phone_number }}</span>
                  <span class="text-gray-500 text-sm">{{ slotProps.option.label || 'No label' }}</span>
                </div>
              </template>
            </Select>
            <small class="text-gray-600">Or manually enter: +country_code_phone (e.g., +923001234567)</small>
            <InputText v-model="testWhatsApp.customPhone" placeholder="Or enter custom number: +923001234567" />
          </div>

          <div class="flex flex-col gap-2">
            <label for="test_message_type">Message Type</label>
            <Select v-model="testWhatsApp.messageType" :options="testMessageTypes" 
              optionLabel="label" optionValue="value" 
              placeholder="Select message type" class="flex-1" />
          </div>

          <div v-if="testWhatsApp.messageType === 'custom'" class="flex flex-col gap-2">
            <label for="test_message">Custom Message</label>
            <textarea v-model="testWhatsApp.customMessage" 
              placeholder="Enter your test message..."
              rows="5"
              class="p-3 border border-gray-300 rounded-md"
            ></textarea>
          </div>

          <div class="result-box" v-if="testWhatsApp.result">
            <p :class="testWhatsApp.result.success ? 'text-green-600' : 'text-red-600'">
              <strong>{{ testWhatsApp.result.success ? '✅ Success!' : '❌ Error!' }}</strong><br/>
              {{ testWhatsApp.result.message }}
            </p>
          </div>

          <div class="flex justify-center gap-3">
            <Button @click="sendTestWhatsApp" label="Send Test Message" icon="pi pi-send" :loading="testWhatsApp.loading" />
            <Button @click="clearTestForm" label="Clear" severity="secondary" outlined />
          </div>
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script>
import axios from '../utils/axios';
import { useRouter } from 'vue-router';
import Card from 'primevue/card';
import Button from 'primevue/button';
import DataTable from 'primevue/datatable';
import Select from 'primevue/select';
import Drawer from 'primevue/drawer';
import Dialog from 'primevue/dialog';
import Column from 'primevue/column';
import Toast from 'primevue/toast';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
export default {
  name: 'HomeView',
  components: {
    Card,
    Button,
    DataTable,
    Column,
    Select,
    Drawer,
    Dialog,
    Toast,
    InputNumber,
    InputText
  },
  data() {
    return {
      user: null,
      showDrawer: false,
      showCreateAlertDialog: false,
      showDeleteAlertDialog: false,
      showUpdateAlertDialog: false,
      showCalculateSharesDialog: false,
      showAddInvestmentDialog: false,
      showInvestmentHistoryDialog: false,
      showPhoneNumbersDialog: false,
      showEmailRecipientsDialog: false,
      showTestWhatsAppDialog: false,
      alerts: [],
      tickers: [],
      investments: [],
      phoneNumbers: [],
      emailRecipients: [],
      selectedAlert: null,
      portfolioPnl: null,
      showComplexity: false,  // Toggle for showing advanced fields
      notificationPreferences: {
        email_notifications_enabled: true,
        whatsapp_notifications_enabled: false
      },
      transactionTypes: [
        { label: 'Add Funds', value: 'add' },
        { label: 'Withdraw Funds', value: 'withdraw' }
      ],
      newPhoneNumber: {
        phone_number: '',
        label: ''
      },
      newEmailRecipient: {
        email: '',
        label: ''
      },
      testMessageTypes: [
        { label: 'Stop Loss Alert Sample', value: 'sl' },
        { label: 'Take Profit Alert Sample', value: 'tp' },
        { label: 'Trailing Stop Sample', value: 'trailing' },
        { label: 'Simple Test Message', value: 'simple' },
        { label: 'Custom Message', value: 'custom' }
      ],
      testWhatsApp: {
        selectedPhone: '',
        customPhone: '',
        messageType: 'simple',
        customMessage: '',
        loading: false,
        result: null
      },
      alert: {
        ticker: "",
        buy_price: 0,
        tp1: null,
        tp2: null,
        tp3: null,
        box_break: null,
        dip_buy: null,
        sl: null,
        shares: null,
        percentage_tp: null,
        percentage_sl: null,
        notes: '',
        trailing_stop_percentage: null
      },
      calcShares: {
        ticker: '',
        current_price: 0,
        amount: null,
        result: 0
      },
      investment: {
        amount: null,
        transaction_type: 'add',
        description: ''
      },
      pollingInterval: null,
      pollingDelay: 30000 // 30 seconds
    };
  },
  mounted() {
    // Get user from localStorage
    const userJson = localStorage.getItem('user');
    if (userJson) {
      this.user = JSON.parse(userJson);
      this.fetchAlerts();
      this.fetchTickers();
      this.fetchPortfolioPnl();
      this.fetchNotificationPreferences();
      // Start polling for alerts
      this.startPolling();
    } else {
      // Redirect to login if no user is found
      this.$router.push('/login');
    }
  },
  beforeUnmount() {
    // Clear polling interval when component is destroyed
    this.stopPolling();
  },
  watch: {
    'alert.ticker': async function (newVal) {
      const response = await this.getSelectedTickerInfo(newVal);
      this.alert.buy_price = Number(response.current);
      console.log(response);
    }
  },
  methods: {
    startPolling() {
      // Clear any existing interval first
      this.stopPolling();
      
      // Set up new polling interval
      this.pollingInterval = setInterval(() => {
        this.fetchAlerts();
        this.fetchPortfolioPnl();
      }, this.pollingDelay);
    },
    
    stopPolling() {
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval);
        this.pollingInterval = null;
      }
    },
    
    async fetchAlerts() {
      try {
        const user_id = this.user.id;
        const response = await axios.get(`/alerts?user_id=${user_id}`);
        this.alerts = response.data;
        // Only show toast when manually refreshing, not during polling
        if (!this.pollingInterval) {
          this.$toast.add({ severity: 'success', summary: 'Success', detail: 'Alerts fetched successfully', life: 3000 });
        }
      } catch (error) {
        console.error('Error fetching alerts:', error);
      }
    },
    async fetchTickers() {
      try {
        const response = await axios.get(`/tickers`);
        this.tickers = response.data;
        console.log(this.tickers);
      } catch (error) {
        console.error('Error fetching tickers:', error);
      }
    },
    validateAlert(alert) {
      if (alert.ticker === "") {
        this.$toast.add({ severity: 'error', summary: 'Error Message', detail: 'Please fill at least the ticker input field', life: 3000 });
        return false;
      }
      return true;
    },
    async createAlert() {
      try {
        if (!this.validateAlert(this.alert)) {
          return;
        }
        const response = await axios.post(`/alert?user_id=${this.user.id}`, this.alert);
        console.log(response.data);
        this.showCreateAlertDialog = false;
        this.alert = {
          ticker: "",
          buy_price: 0,
          tp1: null,
          tp2: null,
          tp3: null,
          box_break: null,
          dip_buy: null,
          sl: null,
          shares: 0,
          percentage_tp: null,
          percentage_sl: null,
          notes: '',
          trailing_stop_percentage: null
        };
        this.fetchAlerts();
        this.$toast.add({ severity: 'success', summary: 'Success Message', detail: 'Alert created successfully', life: 3000 });
      } catch (error) {
        console.error('Error creating alert:', error);
      }
    },
    async updateAlert() {
      if (!this.validateAlert(this.selectedAlert)) {
        return;
      }
      this.selectedAlert.is_sl_hit = false;
      this.selectedAlert.is_tp1_hit = false;
      this.selectedAlert.is_tp2_hit = false;
      this.selectedAlert.is_tp3_hit = false;
      this.selectedAlert.is_dip_buy_hit = false;
      this.selectedAlert.is_box_break_hit = false;
      this.selectedAlert.is_percentage_sl_hit = false;
      this.selectedAlert.is_percentage_tp_hit = false;
      this.selectedAlert.is_trailing_stop_hit = false;
      this.selectedAlert.total_alerts_sent = 0;
      const response = await axios.put(`/alert?user_id=${this.user.id}&alert_id=${this.selectedAlert.id}`, this.selectedAlert);
      this.showUpdateAlertDialog = false;
      console.log(response.data);
      this.$toast.add({ severity: 'success', summary: 'Success Message', detail: 'Alert updated successfully', life: 3000 });
      this.fetchAlerts();
    },
    async deleteAlert(id) {
      const response = await axios.delete(`/alert?user_id=${this.user.id}&alert_id=${id}`);
      this.showDeleteAlertDialog = false;
      console.log(response.data);
      this.$toast.add({ severity: 'success', summary: 'Success Message', detail: 'Alert deleted successfully', life: 3000 });
      this.fetchAlerts();
    },
    async getSelectedTickerInfo(ticker) {
      const response = await axios.get(`/tickers/${ticker}`);
      return response.data;
    },
    logout() {
      // Clear user from localStorage
      localStorage.removeItem('user');
      this.user = null;
      this.stopPolling(); // Stop polling when logging out
      this.$router.push('/login');
    },
    async onCalcTickerChange() {
      if (!this.calcShares.ticker) {
        this.calcShares.current_price = 0;
        this.calcShares.result = 0;
        return;
      }
      const response = await this.getSelectedTickerInfo(this.calcShares.ticker);
      this.calcShares.current_price = Number(response.current);
      console.log(this.calcShares);
      // this.calculateShares();
    },
    calculateShares(value, type) {
      if (type === 'current_price') {
        this.calcShares.current_price = value;
      } else if (type === 'amount') {
        this.calcShares.amount = value;
      }
      console.log(this.calcShares, value, type);
      if (this.calcShares.current_price > 0 && this.calcShares.amount > 0) {
        this.calcShares.result = Number((this.calcShares.amount / this.calcShares.current_price).toFixed(2));
      } else {
        this.calcShares.result = 0;
      }
    },
    async fetchPortfolioPnl() {
      try {
        const response = await axios.get('/portfolio/pnl');
        this.portfolioPnl = response.data;
      } catch (error) {
        console.error('Error fetching portfolio P&L:', error);
      }
    },
    async addInvestment() {
      try {
        if (!this.investment.amount || this.investment.amount <= 0) {
          this.$toast.add({ severity: 'error', summary: 'Error', detail: 'Please enter a valid amount', life: 3000 });
          return;
        }
        await axios.post('/investment', this.investment);
        this.showAddInvestmentDialog = false;
        const transactionType = this.investment.transaction_type;
        this.investment = {
          amount: null,
          transaction_type: 'add',
          description: ''
        };
        this.fetchPortfolioPnl();
        const message = transactionType === 'add' ? 'Funds added successfully' : 'Funds withdrawn successfully';
        this.$toast.add({ severity: 'success', summary: 'Success', detail: message, life: 3000 });
      } catch (error) {
        console.error('Error processing transaction:', error);
        this.$toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to process transaction', life: 3000 });
      }
    },
    async fetchInvestments() {
      try {
        const response = await axios.get('/investments');
        this.investments = response.data;
      } catch (error) {
        console.error('Error fetching investments:', error);
      }
    },
    async openInvestmentHistory() {
      await this.fetchInvestments();
      this.showInvestmentHistoryDialog = true;
    },
    async fetchPhoneNumbers() {
      try {
        const response = await axios.get('/phone-numbers');
        this.phoneNumbers = response.data;
      } catch (error) {
        console.error('Error fetching phone numbers:', error);
      }
    },
    async openPhoneNumbersDialog() {
      await this.fetchPhoneNumbers();
      this.showPhoneNumbersDialog = true;
    },
    async addPhoneNumber() {
      try {
        if (!this.newPhoneNumber.phone_number) {
          this.$toast.add({ severity: 'error', summary: 'Error', detail: 'Please enter a phone number', life: 3000 });
          return;
        }
        
        // Basic validation for phone format
        if (!this.newPhoneNumber.phone_number.startsWith('+')) {
          this.$toast.add({ severity: 'error', summary: 'Error', detail: 'Phone number must start with + and country code', life: 3000 });
          return;
        }
        
        await axios.post('/phone-number', this.newPhoneNumber);
        this.newPhoneNumber = { phone_number: '', label: '' };
        await this.fetchPhoneNumbers();
        this.$toast.add({ severity: 'success', summary: 'Success', detail: 'Phone number added successfully', life: 3000 });
      } catch (error) {
        console.error('Error adding phone number:', error);
        this.$toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to add phone number', life: 3000 });
      }
    },
    async togglePhoneStatus(phone) {
      try {
        await axios.put(`/phone-number/${phone.id}`, { is_active: !phone.is_active });
        await this.fetchPhoneNumbers();
        const status = !phone.is_active ? 'activated' : 'deactivated';
        this.$toast.add({ severity: 'success', summary: 'Success', detail: `Phone number ${status} successfully`, life: 3000 });
      } catch (error) {
        console.error('Error toggling phone status:', error);
        this.$toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to update phone number', life: 3000 });
      }
    },
    async deletePhoneNumber(phoneId) {
      try {
        await axios.delete(`/phone-number/${phoneId}`);
        await this.fetchPhoneNumbers();
        this.$toast.add({ severity: 'success', summary: 'Success', detail: 'Phone number deleted successfully', life: 3000 });
      } catch (error) {
        console.error('Error deleting phone number:', error);
        this.$toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete phone number', life: 3000 });
      }
    },
    async fetchEmailRecipients() {
      try {
        const response = await axios.get('/email-recipients');
        this.emailRecipients = response.data;
      } catch (error) {
        console.error('Error fetching email recipients:', error);
      }
    },
    async openEmailRecipientsDialog() {
      await this.fetchEmailRecipients();
      this.showEmailRecipientsDialog = true;
    },
    async addEmailRecipient() {
      try {
        if (!this.newEmailRecipient.email) {
          this.$toast.add({ severity: 'error', summary: 'Error', detail: 'Please enter an email address', life: 3000 });
          return;
        }
        
        // Basic email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(this.newEmailRecipient.email)) {
          this.$toast.add({ severity: 'error', summary: 'Error', detail: 'Please enter a valid email address', life: 3000 });
          return;
        }
        
        await axios.post('/email-recipient', this.newEmailRecipient);
        this.newEmailRecipient = { email: '', label: '' };
        await this.fetchEmailRecipients();
        this.$toast.add({ severity: 'success', summary: 'Success', detail: 'Email recipient added successfully', life: 3000 });
      } catch (error) {
        console.error('Error adding email recipient:', error);
        this.$toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to add email recipient', life: 3000 });
      }
    },
    async toggleEmailStatus(email) {
      try {
        await axios.put(`/email-recipient/${email.id}`, { is_active: !email.is_active });
        await this.fetchEmailRecipients();
        const status = !email.is_active ? 'activated' : 'deactivated';
        this.$toast.add({ severity: 'success', summary: 'Success', detail: `Email recipient ${status} successfully`, life: 3000 });
      } catch (error) {
        console.error('Error toggling email status:', error);
        this.$toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to update email recipient', life: 3000 });
      }
    },
    async deleteEmailRecipient(emailId) {
      try {
        await axios.delete(`/email-recipient/${emailId}`);
        await this.fetchEmailRecipients();
        this.$toast.add({ severity: 'success', summary: 'Success', detail: 'Email recipient deleted successfully', life: 3000 });
      } catch (error) {
        console.error('Error deleting email recipient:', error);
        this.$toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete email recipient', life: 3000 });
      }
    },
    getTestMessage() {
      const messages = {
        'sl': `🚨 *Stock Alert: AICL* 🚨

📊 Alert Type: Stop Loss
💰 Current Price: PKR 105.50
🎯 Trigger Value: PKR 110.00
📈 Change: -4.09%

⏰ Time: ${new Date().toLocaleString('en-US')}

📝 Notes: This is a test alert`,
        'tp': `🚨 *Stock Alert: AICL* 🚨

📊 Alert Type: Take Profit
💰 Current Price: PKR 125.75
🎯 Trigger Value: PKR 120.00
📈 Change: +4.79%

⏰ Time: ${new Date().toLocaleString('en-US')}

📝 Notes: This is a test alert`,
        'trailing': `🚨 *Stock Alert: AICL* 🚨

📊 Alert Type: Trailing Stop
💰 Current Price: PKR 108.50
🎯 Trigger Value: PKR 115.00
📈 Change: -5.65%

⏰ Time: ${new Date().toLocaleString('en-US')}

📝 Notes: This is a test alert`,
        'simple': `📱 *Test Message from Stock Alert App*

Hello! This is a test WhatsApp message to verify your Twilio integration is working correctly.

✅ If you receive this, your setup is successful!

Time: ${new Date().toLocaleString('en-US')}`,
        'custom': this.testWhatsApp.customMessage
      };
      return messages[this.testWhatsApp.messageType] || messages['simple'];
    },
    async sendTestWhatsApp() {
      try {
        this.testWhatsApp.loading = true;
        this.testWhatsApp.result = null;

        // Determine which phone number to use
        let phoneNumber = this.testWhatsApp.customPhone || this.testWhatsApp.selectedPhone;
        
        if (!phoneNumber) {
          this.$toast.add({ 
            severity: 'error', 
            summary: 'Error', 
            detail: 'Please select or enter a phone number', 
            life: 3000 
          });
          this.testWhatsApp.loading = false;
          return;
        }

        // Validate custom message if custom type is selected
        if (this.testWhatsApp.messageType === 'custom' && !this.testWhatsApp.customMessage.trim()) {
          this.$toast.add({ 
            severity: 'error', 
            summary: 'Error', 
            detail: 'Please enter a custom message', 
            life: 3000 
          });
          this.testWhatsApp.loading = false;
          return;
        }

        const message = this.getTestMessage();

        const response = await axios.post('/test-whatsapp', {
          phone_number: phoneNumber,
          message: message
        });

        this.testWhatsApp.result = {
          success: true,
          message: `Message sent successfully! Check your WhatsApp at ${phoneNumber}`
        };

        this.$toast.add({ 
          severity: 'success', 
          summary: 'Success', 
          detail: 'Test WhatsApp message sent!', 
          life: 5000 
        });

      } catch (error) {
        console.error('Error sending test WhatsApp:', error);
        const errorMessage = error.response?.data?.detail || 'Failed to send test message. Check your Twilio credentials.';
        
        this.testWhatsApp.result = {
          success: false,
          message: errorMessage
        };

        this.$toast.add({ 
          severity: 'error', 
          summary: 'Error', 
          detail: errorMessage, 
          life: 5000 
        });
      } finally {
        this.testWhatsApp.loading = false;
      }
    },
    clearTestForm() {
      this.testWhatsApp = {
        selectedPhone: '',
        customPhone: '',
        messageType: 'simple',
        customMessage: '',
        loading: false,
        result: null
      };
    },
    formatCurrency(value) {
      if (value === null || value === undefined) return '0.00';
      return Number(value).toLocaleString('en-PK', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    },
    async fetchNotificationPreferences() {
      try {
        const response = await axios.get('/notification-preferences');
        this.notificationPreferences = response.data;
      } catch (error) {
        console.error('Error fetching notification preferences:', error);
      }
    },
    async updateNotificationPreferences(field, value) {
      try {
        const update = { [field]: value };
        await axios.put('/notification-preferences', update);
        this.notificationPreferences[field] = value;
        this.$toast.add({ 
          severity: 'success', 
          summary: 'Success', 
          detail: 'Notification preferences updated', 
          life: 3000 
        });
      } catch (error) {
        console.error('Error updating notification preferences:', error);
        this.$toast.add({ 
          severity: 'error', 
          summary: 'Error', 
          detail: 'Failed to update preferences', 
          life: 3000 
        });
      }
    }
  }
}
</script>


<style scoped>
.home-container {
  display: flex;

  min-height: 100vh;
  padding: 1rem;
  background-color: #f5f5f5;
}

.welcome-card {
  width: 100%;
  /* max-width: 600px; */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

.title {
  text-align: center;
  margin: 0;
  color: var(--primary-color);
}

.user-info {
  margin-bottom: 2rem;
}

.user-info h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: var(--text-color);
}

.user-info p {
  margin: 0.5rem 0;
}

.alerts-section {
  margin-bottom: 2rem;
}

.alerts-section h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: var(--text-color);
}

.actions {
  display: flex;
  justify-content: center;
}

.positive-change {
  color: #22c55e;
  font-weight: bold;
}

.negative-change {
  color: #ef4444;
  font-weight: bold;
}

.status-indicators {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
}

.sl-hit {
  background-color: #fee2e2;
  color: #b91c1c;
}

.tp-hit {
  background-color: #dcfce7;
  color: #15803d;
}

.box-break {
  background-color: #e0f2fe;
  color: #0369a1;
}

.dip-buy {
  background-color: #fef3c7;
  color: #92400e;
}

.portfolio-card {
  width: 100%;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.portfolio-summary {
  color: white;
}

.portfolio-summary h3 {
  margin: 0 0 1rem 0;
  font-size: 1.5rem;
  font-weight: bold;
}

.portfolio-stats {
  display: flex;
  justify-content: space-around;
  gap: 2rem;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  text-align: center;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.9;
  font-weight: 500;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
}

.portfolio-info {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.portfolio-info h4 {
  margin: 0 0 1rem 0;
  color: var(--text-color);
}

.transaction-add {
  padding: 0.25rem 0.75rem;
  background-color: #dcfce7;
  color: #15803d;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.875rem;
}

.transaction-withdraw {
  padding: 0.25rem 0.75rem;
  background-color: #fee2e2;
  color: #b91c1c;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.875rem;
}

.investment-history {
  margin-top: 1rem;
}

.phone-numbers-section {
  margin-top: 1rem;
}

.add-phone-form {
  background-color: #f9fafb;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.help-text {
  background-color: #eff6ff;
  padding: 1rem;
  border-radius: 8px;
  border-left: 4px solid #3b82f6;
}

.status-active {
  padding: 0.25rem 0.75rem;
  background-color: #dcfce7;
  color: #15803d;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.875rem;
}

.status-inactive {
  padding: 0.25rem 0.75rem;
  background-color: #fee2e2;
  color: #b91c1c;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.875rem;
}

.test-whatsapp-section {
  margin-top: 1rem;
}

.info-box {
  background-color: #f0f9ff;
  border: 1px solid #bae6fd;
  border-left: 4px solid #0284c7;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.result-box {
  background-color: #f9fafb;
  border: 2px solid #e5e7eb;
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
}

.test-whatsapp-section textarea {
  font-family: inherit;
  resize: vertical;
}

.test-whatsapp-section small {
  display: block;
  margin-top: 0.25rem;
}

/* Toggle Checkbox Styles */
.toggle-checkbox {
  width: 48px;
  height: 24px;
  appearance: none;
  background-color: #cbd5e0;
  border-radius: 12px;
  position: relative;
  cursor: pointer;
  transition: background-color 0.3s;
}

.toggle-checkbox:checked {
  background-color: #667eea;
}

.toggle-checkbox::before {
  content: '';
  position: absolute;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: white;
  top: 2px;
  left: 2px;
  transition: transform 0.3s;
}

.toggle-checkbox:checked::before {
  transform: translateX(24px);
}

/* Notification Preferences Styles */
.notification-preferences {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.notification-preferences h4 {
  margin: 0 0 1rem 0;
  color: var(--text-color);
}

.preference-item {
  margin: 0.75rem 0;
}

.preference-item label {
  cursor: pointer;
  user-select: none;
}
</style>