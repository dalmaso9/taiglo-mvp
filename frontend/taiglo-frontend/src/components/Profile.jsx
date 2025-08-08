import { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { 
  User, Edit, Save, X, Star, MapPin, Calendar, 
  Coffee, Utensils, TreePine, Palette, MessageSquare
} from 'lucide-react'

const API_BASE_URL = 'http://localhost:3000/api'

export default function Profile() {
  const { user, updateProfile } = useAuth()
  const [editing, setEditing] = useState(false)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [userReviews, setUserReviews] = useState([])
  const [reviewsLoading, setReviewsLoading] = useState(true)
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    bio: '',
    date_of_birth: ''
  })

  useEffect(() => {
    if (user) {
      setFormData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        phone: user.phone || '',
        bio: user.bio || '',
        date_of_birth: user.date_of_birth || ''
      })
      fetchUserReviews()
    }
  }, [user])

  const fetchUserReviews = async () => {
    try {
      setReviewsLoading(true)
      const response = await fetch(`${API_BASE_URL}/reviews?user_id=${user.id}&sort_by=created_at&sort_order=desc`)
      if (response.ok) {
        const data = await response.json()
        setUserReviews(data.reviews)
      }
    } catch (error) {
      console.error('Erro ao buscar avaliações do usuário:', error)
    } finally {
      setReviewsLoading(false)
    }
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')

    const result = await updateProfile(formData)
    
    if (result.success) {
      setMessage('Perfil atualizado com sucesso!')
      setEditing(false)
    } else {
      setMessage(result.error)
    }
    
    setLoading(false)
  }

  const handleCancel = () => {
    setFormData({
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      phone: user.phone || '',
      bio: user.bio || '',
      date_of_birth: user.date_of_birth || ''
    })
    setEditing(false)
    setMessage('')
  }

  const getCategoryIcon = (categoryName) => {
    const icons = {
      'Cafés': Coffee,
      'Restaurantes': Utensils,
      'Parques': TreePine,
      'Arte': Palette,
      'Museus': Palette
    }
    return icons[categoryName] || MapPin
  }

  const renderStars = (rating) => {
    return [...Array(5)].map((_, i) => (
      <Star
        key={i}
        className={`h-4 w-4 ${
          i < rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
        }`}
      />
    ))
  }

  if (!user) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Carregando perfil...
          </h3>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Meu Perfil
        </h1>
        <p className="text-gray-600">
          Gerencie suas informações pessoais e veja suas atividades
        </p>
      </div>

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="profile">Informações Pessoais</TabsTrigger>
          <TabsTrigger value="reviews">Minhas Avaliações</TabsTrigger>
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Informações Pessoais</CardTitle>
                  <CardDescription>
                    Atualize suas informações de perfil
                  </CardDescription>
                </div>
                
                {!editing && (
                  <Button onClick={() => setEditing(true)} variant="outline">
                    <Edit className="h-4 w-4 mr-2" />
                    Editar
                  </Button>
                )}
              </div>
            </CardHeader>
            
            <CardContent>
              {message && (
                <Alert className={message.includes('sucesso') ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}>
                  <AlertDescription className={message.includes('sucesso') ? 'text-green-800' : 'text-red-800'}>
                    {message}
                  </AlertDescription>
                </Alert>
              )}

              {editing ? (
                <form onSubmit={handleSubmit} className="space-y-4 mt-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="first_name">Nome</Label>
                      <Input
                        id="first_name"
                        name="first_name"
                        value={formData.first_name}
                        onChange={handleChange}
                        required
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="last_name">Sobrenome</Label>
                      <Input
                        id="last_name"
                        name="last_name"
                        value={formData.last_name}
                        onChange={handleChange}
                        required
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="phone">Telefone</Label>
                    <Input
                      id="phone"
                      name="phone"
                      type="tel"
                      value={formData.phone}
                      onChange={handleChange}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="date_of_birth">Data de Nascimento</Label>
                    <Input
                      id="date_of_birth"
                      name="date_of_birth"
                      type="date"
                      value={formData.date_of_birth}
                      onChange={handleChange}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="bio">Bio</Label>
                    <Textarea
                      id="bio"
                      name="bio"
                      placeholder="Conte um pouco sobre você..."
                      value={formData.bio}
                      onChange={handleChange}
                      rows={4}
                    />
                  </div>
                  
                  <div className="flex space-x-2">
                    <Button type="submit" disabled={loading}>
                      {loading ? (
                        'Salvando...'
                      ) : (
                        <>
                          <Save className="h-4 w-4 mr-2" />
                          Salvar
                        </>
                      )}
                    </Button>
                    
                    <Button type="button" variant="outline" onClick={handleCancel}>
                      <X className="h-4 w-4 mr-2" />
                      Cancelar
                    </Button>
                  </div>
                </form>
              ) : (
                <div className="space-y-6 mt-4">
                  {/* Profile Info Display */}
                  <div className="flex items-center space-x-4">
                    <div className="bg-primary/10 rounded-full p-4">
                      <User className="h-8 w-8 text-primary" />
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900">
                        {user.first_name} {user.last_name}
                      </h3>
                      <p className="text-gray-600">{user.email}</p>
                      {user.is_local_guide && (
                        <Badge className="mt-1">Local Guide</Badge>
                      )}
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div>
                        <Label className="text-sm font-medium text-gray-700">Telefone</Label>
                        <p className="text-gray-900">{user.phone || 'Não informado'}</p>
                      </div>
                      
                      <div>
                        <Label className="text-sm font-medium text-gray-700">Data de Nascimento</Label>
                        <p className="text-gray-900">
                          {user.date_of_birth 
                            ? new Date(user.date_of_birth).toLocaleDateString('pt-BR')
                            : 'Não informado'
                          }
                        </p>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <div>
                        <Label className="text-sm font-medium text-gray-700">Membro desde</Label>
                        <p className="text-gray-900">
                          {new Date(user.created_at).toLocaleDateString('pt-BR')}
                        </p>
                      </div>
                      
                      <div>
                        <Label className="text-sm font-medium text-gray-700">Status</Label>
                        <div className="flex items-center space-x-2">
                          <Badge variant={user.is_verified ? 'default' : 'secondary'}>
                            {user.is_verified ? 'Verificado' : 'Não verificado'}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {user.bio && (
                    <div>
                      <Label className="text-sm font-medium text-gray-700">Bio</Label>
                      <p className="text-gray-900 mt-1">{user.bio}</p>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Reviews Tab */}
        <TabsContent value="reviews">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <MessageSquare className="h-5 w-5" />
                <span>Minhas Avaliações</span>
              </CardTitle>
              <CardDescription>
                Todas as avaliações que você fez no Taiglo
              </CardDescription>
            </CardHeader>
            
            <CardContent>
              {reviewsLoading ? (
                <div className="space-y-4">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="animate-pulse border rounded-lg p-4">
                      <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
                      <div className="h-3 bg-gray-200 rounded w-1/2 mb-3"></div>
                      <div className="h-3 bg-gray-200 rounded"></div>
                    </div>
                  ))}
                </div>
              ) : userReviews.length === 0 ? (
                <div className="text-center py-8">
                  <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Nenhuma avaliação ainda
                  </h3>
                  <p className="text-gray-600">
                    Comece a explorar e avaliar experiências para vê-las aqui!
                  </p>
                </div>
              ) : (
                <div className="space-y-6">
                  {userReviews.map((review) => (
                    <div key={review.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center space-x-1">
                          {renderStars(review.rating)}
                          <span className="ml-2 text-sm text-gray-600">
                            {new Date(review.created_at).toLocaleDateString('pt-BR')}
                          </span>
                        </div>
                        
                        {review.visit_date && (
                          <div className="flex items-center space-x-1 text-sm text-gray-600">
                            <Calendar className="h-3 w-3" />
                            <span>Visitado em {new Date(review.visit_date).toLocaleDateString('pt-BR')}</span>
                          </div>
                        )}
                      </div>
                      
                      {review.title && (
                        <h4 className="font-semibold text-gray-900 mb-2">
                          {review.title}
                        </h4>
                      )}
                      
                      <p className="text-gray-700 mb-3">
                        {review.content}
                      </p>
                      
                      <div className="flex items-center justify-between text-sm text-gray-600">
                        <span>Experiência ID: {review.experience_id}</span>
                        {review.helpful_votes > 0 && (
                          <span>{review.helpful_votes} pessoas acharam útil</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

