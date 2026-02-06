import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import type { 
  PaginatedResponse, 
  ListParams,
  // Core
  User,
  Location,
  Contact,
  Currency,
  TaxType,
  CompanySettings,
  // Genetics
  Strain,
  StrainCategory,
  // Cultivation
  MotherPlant,
  ProductionBatch,
  Clone,
  ProductionAssumption,
  // Inventory
  InventoryAlert,
  StockMovement,
  InventoryAdjustment,
  // Sales
  Customer,
  PriceList,
  Order,
  DeliveryNote,
  SalesInvoice,
  Payment,
  // Purchasing
  Supplier,
  ExpenseCategory,
  PurchaseOrder,
  Expense,
  PurchaseInvoice,
  // HR
  Department,
  Employee,
  PayrollPeriod,
  Payroll,
  // Taxes
  TaxReport,
  TaxJournalEntry,
} from '@/types';

// ============================================
// CORE MODULE HOOKS
// ============================================

// Users
export function useUsers(params?: ListParams) {
  return useQuery({
    queryKey: ['users', params],
    queryFn: () => apiClient.getList<User>('/users/', params),
  });
}

export function useUser(id: number) {
  return useQuery({
    queryKey: ['users', id],
    queryFn: () => apiClient.get<User>(`/users/${id}/`),
    enabled: !!id,
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<User>) => apiClient.post<User>('/users/', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['users'] }),
  });
}

export function useUpdateUser(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<User>) => apiClient.patch<User>(`/users/${id}/`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      queryClient.invalidateQueries({ queryKey: ['users', id] });
    },
  });
}

export function useDeleteUser(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => apiClient.delete(`/users/${id}/`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['users'] }),
  });
}

// Locations
export function useLocations(params?: ListParams) {
  return useQuery({
    queryKey: ['locations', params],
    queryFn: () => apiClient.getList<Location>('/locations/', params),
  });
}

export function useLocation(id: number) {
  return useQuery({
    queryKey: ['locations', id],
    queryFn: () => apiClient.get<Location>(`/locations/${id}/`),
    enabled: !!id,
  });
}

export function useCreateLocation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Location>) => apiClient.post<Location>('/locations/', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['locations'] }),
  });
}

export function useUpdateLocation(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Location>) => apiClient.patch<Location>(`/locations/${id}/`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['locations'] });
      queryClient.invalidateQueries({ queryKey: ['locations', id] });
    },
  });
}

// Contacts
export function useContacts(params?: ListParams) {
  return useQuery({
    queryKey: ['contacts', params],
    queryFn: () => apiClient.getList<Contact>('/contacts/', params),
  });
}

export function useContact(id: number) {
  return useQuery({
    queryKey: ['contacts', id],
    queryFn: () => apiClient.get<Contact>(`/contacts/${id}/`),
    enabled: !!id,
  });
}

export function useCreateContact() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Contact>) => apiClient.post<Contact>('/contacts/', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['contacts'] }),
  });
}

// Currencies
export function useCurrencies(params?: ListParams) {
  return useQuery({
    queryKey: ['currencies', params],
    queryFn: () => apiClient.getList<Currency>('/currencies/', params),
  });
}

// Tax Types
export function useTaxTypes(params?: ListParams) {
  return useQuery({
    queryKey: ['tax-types', params],
    queryFn: () => apiClient.getList<TaxType>('/tax-types/', params),
  });
}

// Company Settings
export function useCompanySettings() {
  return useQuery({
    queryKey: ['company-settings'],
    queryFn: () => apiClient.get<CompanySettings>('/company-settings/1/'),
  });
}

// ============================================
// GENETICS MODULE HOOKS
// ============================================

// Strain Categories
export function useStrainCategories(params?: ListParams) {
  return useQuery({
    queryKey: ['strain-categories', params],
    queryFn: () => apiClient.getList<StrainCategory>('/strain-categories/', params),
  });
}

export function useStrainCategory(id: number) {
  return useQuery({
    queryKey: ['strain-categories', id],
    queryFn: () => apiClient.get<StrainCategory>(`/strain-categories/${id}/`),
    enabled: !!id,
  });
}

export function useCreateStrainCategory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<StrainCategory>) => apiClient.post<StrainCategory>('/strain-categories/', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['strain-categories'] }),
  });
}

// Strains
export function useStrains(params?: ListParams) {
  return useQuery({
    queryKey: ['strains', params],
    queryFn: () => apiClient.getList<Strain>('/strains/', params),
  });
}

export function useStrain(id: number) {
  return useQuery({
    queryKey: ['strains', id],
    queryFn: () => apiClient.get<Strain>(`/strains/${id}/`),
    enabled: !!id,
  });
}

export function useCreateStrain() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Strain>) => apiClient.post<Strain>('/strains/', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['strains'] }),
  });
}

export function useUpdateStrain(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Strain>) => apiClient.patch<Strain>(`/strains/${id}/`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['strains'] });
      queryClient.invalidateQueries({ queryKey: ['strains', id] });
    },
  });
}

export function useDeleteStrain(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => apiClient.delete(`/strains/${id}/`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['strains'] }),
  });
}

// ============================================
// CULTIVATION MODULE HOOKS
// ============================================

// Mother Plants
export function useMotherPlants(params?: ListParams) {
  return useQuery({
    queryKey: ['mother-plants', params],
    queryFn: () => apiClient.getList<MotherPlant>('/mother-plants/', params),
  });
}

export function useMotherPlant(id: number) {
  return useQuery({
    queryKey: ['mother-plants', id],
    queryFn: () => apiClient.get<MotherPlant>(`/mother-plants/${id}/`),
    enabled: !!id,
  });
}

export function useCreateMotherPlant() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<MotherPlant>) => apiClient.post<MotherPlant>('/mother-plants/', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['mother-plants'] }),
  });
}

export function useUpdateMotherPlant(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<MotherPlant>) => apiClient.patch<MotherPlant>(`/mother-plants/${id}/`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mother-plants'] });
      queryClient.invalidateQueries({ queryKey: ['mother-plants', id] });
    },
  });
}

// Production Batches
export function useProductionBatches(params?: ListParams) {
  return useQuery({
    queryKey: ['production-batches', params],
    queryFn: () => apiClient.getList<ProductionBatch>('/production-batches/', params),
  });
}

export function useProductionBatch(id: number) {
  return useQuery({
    queryKey: ['production-batches', id],
    queryFn: () => apiClient.get<ProductionBatch>(`/production-batches/${id}/`),
    enabled: !!id,
  });
}

export function useCreateProductionBatch() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<ProductionBatch>) => apiClient.post<ProductionBatch>('/production-batches/', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['production-batches'] }),
  });
}

export function useCompleteBatch(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => apiClient.post<ProductionBatch>(`/production-batches/${id}/complete_batch/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['production-batches'] });
      queryClient.invalidateQueries({ queryKey: ['production-batches', id] });
      queryClient.invalidateQueries({ queryKey: ['clones'] });
    },
  });
}

// Clones
export function useClones(params?: ListParams) {
  return useQuery({
    queryKey: ['clones', params],
    queryFn: () => apiClient.getList<Clone>('/clones/', params),
  });
}

export function useClone(id: number) {
  return useQuery({
    queryKey: ['clones', id],
    queryFn: () => apiClient.get<Clone>(`/clones/${id}/`),
    enabled: !!id,
  });
}

export function useAvailableClones(params?: { strain?: number; location?: number }) {
  return useQuery({
    queryKey: ['clones', 'available', params],
    queryFn: () => apiClient.getList<Clone>('/clones/available/', params),
  });
}

export function useCreateClone() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Clone>) => apiClient.post<Clone>('/clones/', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['clones'] }),
  });
}

// Production Assumptions
export function useProductionAssumptions(params?: ListParams) {
  return useQuery({
    queryKey: ['production-assumptions', params],
    queryFn: () => apiClient.getList<ProductionAssumption>('/production-assumptions/', params),
  });
}

// ============================================
// INVENTORY MODULE HOOKS
// ============================================

// Inventory Alerts
export function useInventoryAlerts(params?: ListParams) {
  return useQuery({
    queryKey: ['inventory-alerts', params],
    queryFn: () => apiClient.getList<InventoryAlert>('/inventory-alerts/', params),
  });
}

export function useLowStockAlerts() {
  return useQuery({
    queryKey: ['inventory-alerts', 'low-stock'],
    queryFn: () => apiClient.getList<InventoryAlert>('/inventory-alerts/low_stock/'),
  });
}

export function useCreateInventoryAlert() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<InventoryAlert>) => apiClient.post<InventoryAlert>('/inventory-alerts/', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['inventory-alerts'] }),
  });
}

// Stock Movements (Read-only)
export function useStockMovements(params?: ListParams) {
  return useQuery({
    queryKey: ['stock-movements', params],
    queryFn: () => apiClient.getList<StockMovement>('/stock-movements/', params),
  });
}

// Inventory Adjustments
export function useInventoryAdjustments(params?: ListParams) {
  return useQuery({
    queryKey: ['inventory-adjustments', params],
    queryFn: () => apiClient.getList<InventoryAdjustment>('/inventory-adjustments/', params),
  });
}

export function useCreateInventoryAdjustment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<InventoryAdjustment>) => apiClient.post<InventoryAdjustment>('/inventory-adjustments/', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory-adjustments'] });
      queryClient.invalidateQueries({ queryKey: ['clones'] });
      queryClient.invalidateQueries({ queryKey: ['stock-movements'] });
    },
  });
}

// ============================================
// SALES MODULE HOOKS
// ============================================

// Customers
export function useCustomers(params?: ListParams) {
  return useQuery({
    queryKey: ['customers', params],
    queryFn: () => apiClient.getList<Customer>('/customers/', params),
  });
}

export function useCustomer(id: number) {
  return useQuery({
    queryKey: ['customers', id],
    queryFn: () => apiClient.get<Customer>(`/customers/${id}/`),
    enabled: !!id,
  });
}

export function useCreateCustomer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Customer>) => apiClient.post<Customer>('/customers/', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['customers'] }),
  });
}

// Price Lists
export function usePriceLists(params?: ListParams) {
  return useQuery({
    queryKey: ['price-lists', params],
    queryFn: () => apiClient.getList<PriceList>('/price-lists/', params),
  });
}

export function useCreatePriceList() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<PriceList>) => apiClient.post<PriceList>('/price-lists/', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['price-lists'] }),
  });
}

// Orders
export function useOrders(params?: ListParams) {
  return useQuery({
    queryKey: ['orders', params],
    queryFn: () => apiClient.getList<Order>('/orders/', params),
  });
}

export function useOrder(id: number) {
  return useQuery({
    queryKey: ['orders', id],
    queryFn: () => apiClient.get<Order>(`/orders/${id}/`),
    enabled: !!id,
  });
}

export function useCreateOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Order>) => apiClient.post<Order>('/orders/', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['orders'] }),
  });
}

export function useUpdateOrder(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Order>) => apiClient.patch<Order>(`/orders/${id}/`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
      queryClient.invalidateQueries({ queryKey: ['orders', id] });
    },
  });
}

// Delivery Notes
export function useDeliveryNotes(params?: ListParams) {
  return useQuery({
    queryKey: ['delivery-notes', params],
    queryFn: () => apiClient.getList<DeliveryNote>('/delivery-notes/', params),
  });
}

export function useDeliveryNote(id: number) {
  return useQuery({
    queryKey: ['delivery-notes', id],
    queryFn: () => apiClient.get<DeliveryNote>(`/delivery-notes/${id}/`),
    enabled: !!id,
  });
}

export function useCreateDeliveryNote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<DeliveryNote>) => apiClient.post<DeliveryNote>('/delivery-notes/', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['delivery-notes'] }),
  });
}

// Sales Invoices
export function useSalesInvoices(params?: ListParams) {
  return useQuery({
    queryKey: ['sales-invoices', params],
    queryFn: () => apiClient.getList<SalesInvoice>('/sales-invoices/', params),
  });
}

export function useSalesInvoice(id: number) {
  return useQuery({
    queryKey: ['sales-invoices', id],
    queryFn: () => apiClient.get<SalesInvoice>(`/sales-invoices/${id}/`),
    enabled: !!id,
  });
}

export function useCreateSalesInvoice() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<SalesInvoice>) => apiClient.post<SalesInvoice>('/sales-invoices/', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['sales-invoices'] }),
  });
}

// Payments
export function usePayments(params?: ListParams) {
  return useQuery({
    queryKey: ['payments', params],
    queryFn: () => apiClient.getList<Payment>('/payments/', params),
  });
}

export function useCreatePayment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Payment>) => apiClient.post<Payment>('/payments/', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payments'] });
      queryClient.invalidateQueries({ queryKey: ['sales-invoices'] });
    },
  });
}

// ============================================
// PURCHASING MODULE HOOKS
// ============================================

// Suppliers
export function useSuppliers(params?: ListParams) {
  return useQuery({
    queryKey: ['suppliers', params],
    queryFn: () => apiClient.getList<Supplier>('/suppliers/', params),
  });
}

export function useSupplier(id: number) {
  return useQuery({
    queryKey: ['suppliers', id],
    queryFn: () => apiClient.get<Supplier>(`/suppliers/${id}/`),
    enabled: !!id,
  });
}

export function useCreateSupplier() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Supplier>) => apiClient.post<Supplier>('/suppliers/', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['suppliers'] }),
  });
}

// Expense Categories
export function useExpenseCategories(params?: ListParams) {
  return useQuery({
    queryKey: ['expense-categories', params],
    queryFn: () => apiClient.getList<ExpenseCategory>('/expense-categories/', params),
  });
}

export function useCreateExpenseCategory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<ExpenseCategory>) => apiClient.post<ExpenseCategory>('/expense-categories/', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['expense-categories'] }),
  });
}

// Purchase Orders
export function usePurchaseOrders(params?: ListParams) {
  return useQuery({
    queryKey: ['purchase-orders', params],
    queryFn: () => apiClient.getList<PurchaseOrder>('/purchase-orders/', params),
  });
}

export function usePurchaseOrder(id: number) {
  return useQuery({
    queryKey: ['purchase-orders', id],
    queryFn: () => apiClient.get<PurchaseOrder>(`/purchase-orders/${id}/`),
    enabled: !!id,
  });
}

export function useCreatePurchaseOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<PurchaseOrder>) => apiClient.post<PurchaseOrder>('/purchase-orders/', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['purchase-orders'] }),
  });
}

// Expenses
export function useExpenses(params?: ListParams) {
  return useQuery({
    queryKey: ['expenses', params],
    queryFn: () => apiClient.getList<Expense>('/expenses/', params),
  });
}

export function useCreateExpense() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Expense>) => apiClient.post<Expense>('/expenses/', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['expenses'] }),
  });
}

// Purchase Invoices
export function usePurchaseInvoices(params?: ListParams) {
  return useQuery({
    queryKey: ['purchase-invoices', params],
    queryFn: () => apiClient.getList<PurchaseInvoice>('/purchase-invoices/', params),
  });
}

export function usePurchaseInvoice(id: number) {
  return useQuery({
    queryKey: ['purchase-invoices', id],
    queryFn: () => apiClient.get<PurchaseInvoice>(`/purchase-invoices/${id}/`),
    enabled: !!id,
  });
}

export function useCreatePurchaseInvoice() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<PurchaseInvoice>) => apiClient.post<PurchaseInvoice>('/purchase-invoices/', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['purchase-invoices'] }),
  });
}

// ============================================
// HR MODULE HOOKS
// ============================================

// Departments
export function useDepartments(params?: ListParams) {
  return useQuery({
    queryKey: ['departments', params],
    queryFn: () => apiClient.getList<Department>('/departments/', params),
  });
}

export function useCreateDepartment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Department>) => apiClient.post<Department>('/departments/', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['departments'] }),
  });
}

// Employees
export function useEmployees(params?: ListParams) {
  return useQuery({
    queryKey: ['employees', params],
    queryFn: () => apiClient.getList<Employee>('/employees/', params),
  });
}

export function useEmployee(id: number) {
  return useQuery({
    queryKey: ['employees', id],
    queryFn: () => apiClient.get<Employee>(`/employees/${id}/`),
    enabled: !!id,
  });
}

export function useCreateEmployee() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Employee>) => apiClient.post<Employee>('/employees/', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['employees'] }),
  });
}

// Payroll Periods
export function usePayrollPeriods(params?: ListParams) {
  return useQuery({
    queryKey: ['payroll-periods', params],
    queryFn: () => apiClient.getList<PayrollPeriod>('/payroll-periods/', params),
  });
}

export function useCreatePayrollPeriod() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<PayrollPeriod>) => apiClient.post<PayrollPeriod>('/payroll-periods/', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['payroll-periods'] }),
  });
}

// Payrolls
export function usePayrolls(params?: ListParams) {
  return useQuery({
    queryKey: ['payrolls', params],
    queryFn: () => apiClient.getList<Payroll>('/payrolls/', params),
  });
}

export function usePayroll(id: number) {
  return useQuery({
    queryKey: ['payrolls', id],
    queryFn: () => apiClient.get<Payroll>(`/payrolls/${id}/`),
    enabled: !!id,
  });
}

export function useCreatePayroll() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Payroll>) => apiClient.post<Payroll>('/payrolls/', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['payrolls'] }),
  });
}

// ============================================
// TAXES MODULE HOOKS
// ============================================

// Tax Reports
export function useTaxReports(params?: ListParams) {
  return useQuery({
    queryKey: ['tax-reports', params],
    queryFn: () => apiClient.getList<TaxReport>('/tax-reports/', params),
  });
}

export function useTaxReport(id: number) {
  return useQuery({
    queryKey: ['tax-reports', id],
    queryFn: () => apiClient.get<TaxReport>(`/tax-reports/${id}/`),
    enabled: !!id,
  });
}

export function useCreateTaxReport() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<TaxReport>) => apiClient.post<TaxReport>('/tax-reports/', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['tax-reports'] }),
  });
}

export function useCalculateTaxTotals(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => apiClient.post<TaxReport>(`/tax-reports/${id}/calculate_totals/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tax-reports'] });
      queryClient.invalidateQueries({ queryKey: ['tax-reports', id] });
    },
  });
}

// Tax Journal Entries
export function useTaxJournalEntries(params?: ListParams) {
  return useQuery({
    queryKey: ['tax-journal-entries', params],
    queryFn: () => apiClient.getList<TaxJournalEntry>('/tax-journal-entries/', params),
  });
}

export function useCreateTaxJournalEntry() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<TaxJournalEntry>) => apiClient.post<TaxJournalEntry>('/tax-journal-entries/', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['tax-journal-entries'] }),
  });
}

