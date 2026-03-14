# Phase 2: Real Affiliate Network Integrations
## Connecting to Amazon, CJ, Rakuten, Shopify APIs

**Status:** Planning Document (Not Yet Implemented)
**Priority:** HIGH - Unlocks real revenue
**Timeline:** 2-3 weeks implementation

---

## 🎯 Phase 2 Objectives

1. Connect to real affiliate network APIs
2. Automatically sync commissions to NexusFlow
3. Apply automatic 40/60 profit-sharing split
4. Show users real earnings on dashboard
5. Collect platform's 40% revenue
6. Enable payout system for users

---

## 📋 Affiliate Networks to Integrate

### 1. Amazon Associate (PA-API v5) - CRITICAL
**Why First:** Largest commission volume, most users have accounts

**Integration Pattern:**
```python
# File: apps/engine/core/channels/amazon_affiliate.py

import boto3
from datetime import datetime, timedelta

class AmazonAffiliateSync:
    def __init__(self, access_key, secret_key, partner_tag):
        self.client = boto3.client('paapi5',
            region_name='us-east-1',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key)
        self.partner_tag = partner_tag

    def get_commissions(self, days=7):
        """
        Fetch commissions for last N days from Amazon.

        Returns:
            [
                {
                    "commission_id": "amz_123",
                    "amount": 45.50,
                    "product": "MacBook Pro",
                    "date": "2024-03-08",
                    "status": "approved"  # or "pending"
                },
                ...
            ]
        """
        # Use Amazon's Reporting API to get earnings
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Call Amazon API
        response = self.client.get_report_data(
            ReportType='AmazonAssociatesEarnings',
            StartDate=start_date.isoformat(),
            EndDate=end_date.isoformat(),
        )

        commissions = []
        for item in response.get('Items', []):
            if item.get('Status') == 'Approved':
                commissions.append({
                    'commission_id': item.get('EarningId'),
                    'amount': float(item.get('Amount')),
                    'product': item.get('ProductName'),
                    'date': item.get('DateEarned').date(),
                })

        return commissions

    def sync_for_user(self, db: Session, user: User):
        """Sync commissions for a specific user."""
        from apps.engine.core.ledger_service import LedgerService

        # Get user's Amazon affiliate account info
        affiliate_account = db.query(AffiliateNetwork).filter(
            AffiliateNetwork.user_id == user.id,
            AffiliateNetwork.network_name == "amazon"
        ).first()

        if not affiliate_account or not affiliate_account.api_key:
            return {"status": "skipped", "reason": "No Amazon account connected"}

        # Get commissions from Amazon
        try:
            commissions = self.get_commissions(days=7)
        except Exception as e:
            logger.error(f"Amazon API error: {e}")
            return {"status": "error", "message": str(e)}

        # Record each commission with automatic 40/60 split
        recorded_count = 0
        for commission in commissions:
            try:
                entry, breakdown = LedgerService.record_affiliate_commission(
                    db=db,
                    user_id=user.id,
                    gross_revenue=commission['amount'],
                    affiliate_network="amazon",
                    affiliate_source=commission['product'],
                    affiliate_id=commission['commission_id'],
                    description=f"Amazon commission for {commission['product']}"
                )
                recorded_count += 1
                logger.info(f"Recorded Amazon commission: ${commission['amount']}")
            except Exception as e:
                logger.error(f"Failed to record commission: {e}")

        return {
            "status": "success",
            "network": "amazon",
            "commissions_synced": recorded_count,
            "total_amount": sum(c['amount'] for c in commissions),
        }
```

**Setup Required:**
1. Get AWS Access Key + Secret Key from Amazon Associates account
2. Create Partner Tag (e.g., "nexusflow-20")
3. Store encrypted in database via AffiliateNetwork model
4. User connects account via `/affiliate-networks/connect/amazon`

**API Reference:** https://webservices.amazon.com/paapi5/documentation/

---

### 2. CJ Affiliate (Commission Junction) - HIGH PRIORITY
**Why:** Thousands of merchants, high commission rates

**Integration Pattern:**
```python
# File: apps/engine/core/channels/cj_affiliate.py

import requests
from datetime import datetime, timedelta

class CJAffiliateSync:
    BASE_URL = "https://apis.cj.com/v2"

    def __init__(self, api_token):
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Accept": "application/json"
        }

    def get_commissions(self, days=7):
        """
        Fetch commissions from CJ Affiliate.

        CJ API returns earnings with merchant info, product details, dates, etc.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # CJ Affiliate Earnings API endpoint
        url = f"{self.BASE_URL}/earnings"
        params = {
            "start-date": start_date.strftime("%Y-%m-%d"),
            "end-date": end_date.strftime("%Y-%m-%d"),
            "status": "approved",  # Only approved commissions
        }

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        commissions = []
        for earning in response.json().get('earnings', []):
            commissions.append({
                'commission_id': earning.get('id'),
                'amount': float(earning.get('amount', {}).get('amount')),
                'product': earning.get('product', {}).get('name'),
                'merchant': earning.get('advertiser', {}).get('name'),
                'date': earning.get('date'),
            })

        return commissions

    def sync_for_user(self, db: Session, user: User):
        """Sync CJ commissions for user."""
        from apps.engine.core.ledger_service import LedgerService

        affiliate_account = db.query(AffiliateNetwork).filter(
            AffiliateNetwork.user_id == user.id,
            AffiliateNetwork.network_name == "cj_affiliate"
        ).first()

        if not affiliate_account or not affiliate_account.api_key:
            return {"status": "skipped"}

        try:
            commissions = self.get_commissions()
        except requests.RequestException as e:
            return {"status": "error", "message": str(e)}

        recorded = 0
        for commission in commissions:
            try:
                entry, breakdown = LedgerService.record_affiliate_commission(
                    db=db,
                    user_id=user.id,
                    gross_revenue=commission['amount'],
                    affiliate_network="cj_affiliate",
                    affiliate_source=f"{commission['product']} ({commission['merchant']})",
                    affiliate_id=commission['commission_id'],
                )
                recorded += 1
            except Exception as e:
                logger.error(f"CJ sync error: {e}")

        return {
            "status": "success",
            "network": "cj_affiliate",
            "commissions_synced": recorded
        }
```

**Setup Required:**
1. Get API token from CJ Affiliate account settings
2. Store in AffiliateNetwork.api_key (encrypted)
3. User connects account via `/affiliate-networks/connect/cj`

**API Reference:** https://help.cj.com/en/articles/

---

### 3. Rakuten Affiliate - MEDIUM PRIORITY
**Why:** Large merchant network, good commission rates

**Integration Pattern:**
```python
# File: apps/engine/core/channels/rakuten_affiliate.py

import requests

class RakutenAffiliateSync:
    BASE_URL = "https://api.linkshare.com"

    def __init__(self, api_token):
        self.api_token = api_token

    def get_commissions(self, days=7):
        """Fetch Rakuten commissions."""
        # Rakuten API endpoint for commissions
        url = f"{self.BASE_URL}/1.0/commissions"

        params = {
            "token": self.api_token,
            "daterange": f"lastdays({days})",
            "format": "json"
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        commissions = []
        for item in response.json().get('commissions', []):
            commissions.append({
                'commission_id': item.get('commission_id'),
                'amount': float(item.get('commission_amount')),
                'merchant': item.get('merchant_name'),
                'date': item.get('transaction_date'),
            })

        return commissions

    def sync_for_user(self, db: Session, user: User):
        """Similar to Amazon/CJ pattern..."""
        # Implementation follows same pattern
        pass
```

---

### 4. Shopify Affiliate - MEDIUM PRIORITY
**Why:** For users who run own stores

**Integration Pattern:**
```python
# File: apps/engine/core/channels/shopify_affiliate.py

import shopify

class ShopifyAffiliateSync:
    def __init__(self, shop_url, access_token):
        shopify.ShopifyResource.set_site(f"https://{access_token}@{shop_url}/admin/api/2024-01.json")

    def get_affiliate_revenue(self, days=7):
        """Get affiliate commissions from Shopify store."""
        # Shopify doesn't have native affiliate tracking
        # But we can sync sales attributed to affiliate links

        # Implementation would:
        # 1. Query recent orders with affiliate tracking params
        # 2. Calculate commission (store owner defines %)
        # 3. Return as commission entries
        pass
```

---

## 🔄 Sync Architecture

### Automatic Sync Scheduler
```python
# File: apps/engine/core/affiliate_sync_scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from apps.engine.db.session import SessionLocal
from apps.engine.db.models import User, AffiliateNetwork
from apps.engine.core.channels.amazon_affiliate import AmazonAffiliateSync
from apps.engine.core.channels.cj_affiliate import CJAffiliateSync

scheduler = BackgroundScheduler()

def sync_all_affiliate_networks():
    """
    Called daily at 2 AM to sync all user affiliate accounts.
    Automatically applies 40/60 profit-sharing split.
    """
    db = SessionLocal()
    try:
        # Get all users with connected affiliate accounts
        users_with_affiliates = db.query(User).join(
            AffiliateNetwork
        ).distinct().all()

        for user in users_with_affiliates:
            sync_user_affiliates(db, user)
    finally:
        db.close()

def sync_user_affiliates(db: Session, user: User):
    """Sync all affiliate networks for a single user."""

    # Get all connected networks for this user
    networks = db.query(AffiliateNetwork).filter(
        AffiliateNetwork.user_id == user.id,
        AffiliateNetwork.is_active == True
    ).all()

    results = {}

    for network_config in networks:
        network_name = network_config.network_name

        if network_name == "amazon":
            amazon_sync = AmazonAffiliateSync(
                decrypt_token(network_config.api_key)
            )
            result = amazon_sync.sync_for_user(db, user)

        elif network_name == "cj_affiliate":
            cj_sync = CJAffiliateSync(
                decrypt_token(network_config.api_key)
            )
            result = cj_sync.sync_for_user(db, user)

        # Similar for Rakuten, Shopify

        results[network_name] = result

        # Update last_synced timestamp
        network_config.last_synced = datetime.now()
        db.commit()

    logger.info(f"Synced user {user.email}: {results}")

# Schedule sync for every day at 2 AM
scheduler.add_job(sync_all_affiliate_networks, 'cron', hour=2, minute=0)
scheduler.start()
```

**In `apps/engine/main.py` startup:**
```python
from apps.engine.core.affiliate_sync_scheduler import scheduler

# Start scheduler when app starts
scheduler.start()
```

---

## 📱 User Flow for Connecting Affiliate Accounts

### 1. User Sees "Connect Affiliate Accounts" Button
On dashboard under "Earnings"

### 2. User Clicks "Connect Amazon"
- Redirects to Amazon Associates login
- Authorizes NexusFlow to read earnings
- Returns to NexusFlow with access token
- NexusFlow stores encrypted token in `AffiliateNetwork` table

### 3. NexusFlow Syncs Automatically
- Every day at 2 AM, cron job runs
- Fetches all commissions from Amazon API
- Applies automatic 40/60 split
- Records in ledger with balance snapshot
- Updates `AffiliateNetwork.total_earnings`

### 4. User Sees Real Earnings
- Dashboard shows real money flowing in
- Earnings breakdown by network
- Projected monthly earnings
- Payout options

---

## 💰 Revenue Impact

### Before (Old Model)
```
Platform Revenue: $0 (users don't earn, don't deposit, don't stay)
User Revenue: -$250 (lose deposit)
```

### After Phase 2 (Real Integrations)
```
Assuming:
- 1,000 users after 6 months
- Each user earning $300/month on average
- From affiliate commissions

Monthly Gross Affiliate Commissions: 1,000 × $300 = $300,000
Platform Takes 40%: $120,000/month = $1,440,000/year
User Earnings (60%): $180,000/month = $2,160,000/year

Both sides are happy!
```

---

## 🔐 Security Considerations

### API Key Storage
```python
from apps.engine.core.security import encrypt_token, decrypt_token

# Store encrypted
network.api_key = encrypt_token(user_provided_token)

# Retrieve decrypted
token = decrypt_token(network.api_key)

# Never log the token
```

### Rate Limiting
```python
# Amazon: 1 request per second max
# CJ: 10 requests per second max
# Rakuten: 5 requests per second max
# Implement backoff logic if rate limited
```

### Error Handling
```python
try:
    commissions = sync_commissions()
except RateLimitError:
    # Back off and retry later
    schedule_retry(user_id, 300)  # Retry in 5 min
except AuthenticationError:
    # Notify user to re-authenticate
    notify_user_reconnect_needed(user)
except Exception as e:
    # Log and continue (don't break other users)
    logger.error(f"Sync error: {e}")
```

---

## 📊 Metrics to Track

### Per-User
- Commissions synced this month
- Revenue by affiliate network
- Pending vs approved commissions
- Payout readiness
- Last sync timestamp

### Platform-Wide
- Total commissions fetched
- Total platform fees collected (40%)
- Total user earnings (60%)
- Failed syncs (by reason)
- Sync latency
- API error rates

---

## ✅ Phase 2 Implementation Checklist

- [ ] Implement Amazon PA-API integration
- [ ] Implement CJ Affiliate integration
- [ ] Implement Rakuten integration
- [ ] Create daily sync scheduler
- [ ] Add `AffiliateNetwork` connection UI
- [ ] Update earnings dashboard with real data
- [ ] Add payout system
- [ ] Test with real affiliate accounts
- [ ] Load test with 1000+ users
- [ ] Deploy to production
- [ ] Monitor first real commissions
- [ ] Announce to users

---

## 🎯 Success Metrics for Phase 2

- First affiliate commission recorded: ✅ Date TBD
- Users with connected accounts: Target 20% of active users
- Monthly affiliate volume: Target $100K gross commissions
- Platform monthly revenue (40%): Target $40K
- Sync success rate: Target 99%+

---

## 📚 Resources

- Amazon PA-API: https://webservices.amazon.com/paapi5/
- CJ Affiliate Docs: https://help.cj.com/
- Rakuten API: https://help.rakuten.com/
- APScheduler: https://apscheduler.readthedocs.io/
- SQLAlchemy Encryption: https://sqlalchemy.org/

---

**Next Phase Status:** Ready for implementation once Phase 1 is deployed
