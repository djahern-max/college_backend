from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings

# For now, let's use synchronous database operations to avoid asyncpg issues
# We can switch back to async once we resolve the Python 3.13 compatibility

# Create synchronous engine 
engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all our database models
Base = declarative_base()

# For async operations (when asyncpg is working)
try:
    # Convert PostgreSQL URL to async version
    async_database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    
    # Create async engine
    async_engine = create_async_engine(
        async_database_url,
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )
    
    # Create async session factory
    AsyncSessionLocal = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    ASYNC_AVAILABLE = True
    
except ImportError:
    print("⚠️  AsyncPG not available, using synchronous database operations")
    ASYNC_AVAILABLE = False
    async_engine = None
    AsyncSessionLocal = None


# Dependency function to get database session
async def get_db():
    """
    Dependency that provides a database session to route functions.
    Falls back to sync operations if async is not available.
    """
    if ASYNC_AVAILABLE and AsyncSessionLocal:
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    else:
        # Fallback to synchronous operations
        db = SessionLocal()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()


# Initialize database tables
async def init_db():
    """Initialize database tables"""
    try:
        if ASYNC_AVAILABLE and async_engine:
            async with async_engine.begin() as conn:
                from app.models import user, profile, oauth  # noqa
                await conn.run_sync(Base.metadata.create_all)
        else:
            # Use synchronous creation
            from app.models import user, profile, oauth  # noqa
            Base.metadata.create_all(bind=engine)
        
        print("✅ Database tables initialized successfully!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("📝 Make sure PostgreSQL is running and database exists")


# Health check function
async def check_db_connection():
    """Check if database connection is working"""
    try:
        if ASYNC_AVAILABLE and AsyncSessionLocal:
            async with AsyncSessionLocal() as session:
                result = await session.execute("SELECT 1")
                return True
        else:
            # Synchronous health check
            db = SessionLocal()
            try:
                db.execute("SELECT 1")
                return True
            finally:
                db.close()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
