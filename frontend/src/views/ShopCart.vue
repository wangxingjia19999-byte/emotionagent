<template>
  <div class="cart-page">
    <section class="cart-header glass-card">
      <div>
        <span class="page-kicker">Cart</span>
        <h1>购物车</h1>
        <p>确认好要带走的解压好物，然后去结算吧。</p>
      </div>
    </section>

    <section class="cart-body glass-card" v-loading="loading">
      <template v-if="cartItems.length">
        <div class="cart-list">
          <div v-for="item in cartItems" :key="item.id" class="cart-item">
            <div class="cart-item__image" @click="$router.push(`/shop/${item.product_id}`)">
              <el-image :src="item.product?.image_url" fit="cover">
                <template #error>
                  <div class="cart-item__placeholder">
                    <el-icon :size="30"><Present /></el-icon>
                  </div>
                </template>
              </el-image>
            </div>

            <div class="cart-item__info" @click="$router.push(`/shop/${item.product_id}`)">
              <h3>{{ item.product?.name || '商品已下架' }}</h3>
              <span class="cart-item__type">{{ item.product?.product_type === 'service' ? '服务' : '实物' }}</span>
            </div>

            <div class="cart-item__price">¥{{ item.product?.price }}</div>

            <div class="cart-item__quantity">
              <el-input-number
                v-model="item.quantity"
                :min="1"
                :max="item.product?.product_type === 'physical' ? item.product?.stock || 1 : 99"
                size="small"
                @change="handleQuantityChange(item)"
              />
            </div>

            <div class="cart-item__subtotal">
              ¥{{ ((item.product?.price || 0) * item.quantity).toFixed(2) }}
            </div>

            <el-button class="cart-item__remove" type="danger" link @click="handleRemove(item)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>

        <div class="cart-summary">
          <div class="cart-summary__total">
            合计：<strong>¥{{ totalAmount.toFixed(2) }}</strong>
          </div>
          <el-button class="cart-summary__checkout" @click="showCheckout = true">
            去结算
          </el-button>
        </div>
      </template>

      <EmptyState
        v-else
        title="购物车是空的"
        description="去看看有什么喜欢的解压好物吧。"
        action-text="逛逛商城"
        @action="$router.push('/shop')"
      />
    </section>

    <!-- 结算弹窗 -->
    <el-dialog v-model="showCheckout" title="确认订单" width="560px" :lock-scroll="true" destroy-on-close>
      <div v-if="hasPhysical" class="checkout-address">
        <div class="checkout-address__header">
          <strong>收货地址</strong>
          <el-button size="small" text type="primary" @click="showAddressForm = true">+ 新增</el-button>
        </div>
        <el-radio-group v-model="selectedAddressId" class="checkout-address__list">
          <div v-for="addr in addresses" :key="addr.id" class="checkout-address__item">
            <el-radio :label="addr.id" :value="addr.id">
              {{ addr.receiver_name }} {{ addr.phone }}
              <br />
              <small>{{ addr.province }}{{ addr.city }}{{ addr.district }} {{ addr.detail }}</small>
            </el-radio>
          </div>
        </el-radio-group>
        <div v-if="!addresses.length" class="checkout-address__empty">
          暂无地址，请先新增收货地址
        </div>
      </div>

      <div class="checkout-items">
        <strong>订单商品</strong>
        <div v-for="item in cartItems" :key="item.id" class="checkout-items__row">
          <span>{{ item.product?.name }} × {{ item.quantity }}</span>
          <span>¥{{ ((item.product?.price || 0) * item.quantity).toFixed(2) }}</span>
        </div>
      </div>

      <div class="checkout-total">
        应付金额：<strong>¥{{ totalAmount.toFixed(2) }}</strong>
      </div>

      <template #footer>
        <el-button @click="showCheckout = false">取消</el-button>
        <el-button class="checkout-submit" @click="handleCheckout" :loading="submitting">
          确认下单
        </el-button>
      </template>
    </el-dialog>

    <!-- 新增地址弹窗 -->
    <el-dialog v-model="showAddressForm" title="新增收货地址" width="480px" :lock-scroll="true">
      <el-form :model="addressForm" label-width="80px" label-position="top">
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="收件人">
              <el-input v-model="addressForm.receiver_name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="手机号">
              <el-input v-model="addressForm.phone" placeholder="请输入手机号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="省份">
              <el-input v-model="addressForm.province" placeholder="省" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="城市">
              <el-input v-model="addressForm.city" placeholder="市" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="区/县">
              <el-input v-model="addressForm.district" placeholder="区/县" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="详细地址">
          <el-input v-model="addressForm.detail" placeholder="街道、门牌号等" />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="addressForm.is_default" :true-label="1" :false-label="0">设为默认地址</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddressForm = false">取消</el-button>
        <el-button class="checkout-submit" @click="handleSaveAddress" :loading="savingAddress">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Present } from '@element-plus/icons-vue'
import { getCart, updateCartItem, removeCartItem, getAddresses, createAddress, createOrder } from '../api/shop'
import EmptyState from '../components/EmptyState.vue'

const router = useRouter()
const loading = ref(false)
const cartItems = ref([])
const showCheckout = ref(false)
const showAddressForm = ref(false)
const submitting = ref(false)
const savingAddress = ref(false)
const addresses = ref([])
const selectedAddressId = ref(null)

const addressForm = reactive({
  receiver_name: '', phone: '', province: '', city: '', district: '', detail: '',
  is_default: 0,
})

const hasPhysical = computed(() =>
  cartItems.value.some(i => i.product?.product_type === 'physical')
)

const totalAmount = computed(() =>
  cartItems.value.reduce((s, i) => s + (i.product?.price || 0) * i.quantity, 0)
)

async function fetchCart() {
  loading.value = true
  try {
    const res = await getCart()
    cartItems.value = res.data.items || []
  } finally {
    loading.value = false
  }
}

async function fetchAddresses() {
  const res = await getAddresses()
  addresses.value = res.data || []
  const def = addresses.value.find(a => a.is_default)
  if (def) selectedAddressId.value = def.id
}

function handleQuantityChange(item) {
  updateCartItem(item.id, { quantity: item.quantity }).catch(() => {})
}

async function handleRemove(item) {
  try {
    await ElMessageBox.confirm('确定要移除这个商品吗？', '提示', { type: 'warning' })
  } catch { return }
  await removeCartItem(item.id)
  ElMessage.success('已移除')
  fetchCart()
}

async function handleSaveAddress() {
  savingAddress.value = true
  try {
    await createAddress({ ...addressForm })
    ElMessage.success('地址已保存')
    showAddressForm.value = false
    fetchAddresses()
    // reset form
    Object.assign(addressForm, {
      receiver_name: '', phone: '', province: '', city: '', district: '', detail: '',
      is_default: 0,
    })
  } finally {
    savingAddress.value = false
  }
}

async function handleCheckout() {
  if (hasPhysical.value && !selectedAddressId.value) {
    ElMessage.warning('请选择收货地址')
    return
  }
  submitting.value = true
  try {
    const payload = { payment_method: 'mock' }
    if (selectedAddressId.value) payload.address_id = selectedAddressId.value
    await createOrder(payload)
    ElMessage.success('下单成功')
    showCheckout.value = false
    router.push('/shop/orders')
  } catch { /* error handled by interceptor */ }
  finally { submitting.value = false }
}

onMounted(() => { fetchCart(); fetchAddresses() })
</script>

<style scoped>
.cart-page { display: grid; gap: 16px; }

.glass-card {
  border-radius: 24px;
  border: 1px solid #e8ebf3;
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 14px 30px rgba(44, 52, 73, 0.06);
  padding: 22px 26px;
}

.page-kicker {
  display: inline-flex;
  min-height: 28px;
  align-items: center;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  color: #6074df;
  background: #edf2ff;
}

.cart-header h1 { margin: 10px 0 0; font-size: 24px; color: #243042; }
.cart-header p { margin: 8px 0 0; color: #6a7281; }

.cart-body { min-height: 300px; }

.cart-item {
  display: flex; align-items: center; gap: 14px;
  padding: 16px 0; border-bottom: 1px solid #f0f2f7;
}

.cart-item__image {
  width: 80px; height: 80px; border-radius: 14px;
  overflow: hidden; background: #f4f6fb; cursor: pointer; flex-shrink: 0;
}

.cart-item__image :deep(.el-image) { width: 100%; height: 100%; }

.cart-item__placeholder {
  width: 100%; height: 100%;
  display: grid; place-items: center; color: #c0c7d2;
}

.cart-item__info { flex: 1; cursor: pointer; min-width: 0; }

.cart-item__info h3 {
  margin: 0; font-size: 14px; color: #243042;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

.cart-item__type { font-size: 12px; color: #8991a2; }

.cart-item__price { font-size: 15px; font-weight: 600; color: #243042; width: 80px; text-align: center; }

.cart-item__quantity { width: 110px; display: flex; justify-content: center; }

.cart-item__subtotal { font-size: 16px; font-weight: 700; color: #6074df; width: 80px; text-align: right; }

.cart-item__remove { flex-shrink: 0; }

.cart-summary {
  display: flex; align-items: center; justify-content: flex-end;
  gap: 18px; padding-top: 20px;
}

.cart-summary__total { font-size: 16px; color: #243042; }

.cart-summary__total strong { font-size: 22px; color: #6074df; }

.cart-summary__checkout {
  min-height: 44px; padding: 0 32px;
  border-radius: 14px; border: none; color: #ffffff; font-size: 15px;
  background: linear-gradient(135deg, #6f84e8 0%, #7a92ee 100%);
}

/* checkout dialog */
.checkout-address { margin-bottom: 20px; }

.checkout-address__header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }

.checkout-address__list { display: grid; gap: 8px; }

.checkout-address__item { padding: 12px 14px; border-radius: 12px; background: #f8f9fc; }

.checkout-address__item small { color: #8991a2; }

.checkout-address__empty { padding: 20px; text-align: center; color: #c0c7d2; }

.checkout-items { margin-bottom: 16px; }

.checkout-items strong { display: block; margin-bottom: 10px; }

.checkout-items__row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 8px 0; font-size: 14px; color: #526073;
}

.checkout-total { text-align: right; font-size: 16px; color: #243042; }

.checkout-total strong { font-size: 22px; color: #6074df; }

.checkout-submit {
  border: none; color: #ffffff;
  background: linear-gradient(135deg, #6f84e8 0%, #7a92ee 100%);
  border-radius: 12px;
}
</style>
